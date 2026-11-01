"""Formulário de criação de Registro Clínico pelo Profissional autenticado."""

import streamlit as st

from . import sessao
from .cache_xano import invalidar_cache
from .api import ErroAcesso

_CHAVE_CACHE = "prontuario_historico_cache"
_CHAVE_ABERTO = "prontuario_nova_evolucao_aberta"


def _limpar_formulario():
    for chave in ("nova-evolucao-paciente", "nova-evolucao-consulta", "nova-evolucao-conteudo"):
        st.session_state.pop(chave, None)
    st.session_state.pop(_CHAVE_ABERTO, None)


def _abrir_formulario():
    _limpar_formulario()
    st.session_state[_CHAVE_ABERTO] = True


def _trocar_paciente():
    st.session_state.pop("nova-evolucao-consulta", None)
    st.session_state.pop("nova-evolucao-conteudo", None)


def _consultas_paciente(consultas, paciente_id):
    return [consulta for consulta in consultas if consulta.get("paciente_id") == paciente_id]


def renderizar(cliente, conta, consultas):
    """Exibe a ação e coleta os dados aceitos pelo contrato REST existente."""
    perfis = set(getattr(conta, "perfis", ()))
    if "profissional" not in perfis:
        _limpar_formulario()
        st.warning("Somente Profissional autorizado pode registrar uma evolução clínica.")
        return

    credencial = st.session_state.get(sessao.CHAVE)
    if not credencial:
        _limpar_formulario()
        st.error("Sua sessão não está disponível. Entre novamente.")
        return

    if not st.session_state.get(_CHAVE_ABERTO):
        st.button("Nova evolução", type="primary", key="prontuario-nova-evolucao",
                  on_click=_abrir_formulario)
        return

    pacientes = {}
    for consulta in consultas:
        paciente_id = consulta.get("paciente_id")
        nome = consulta.get("paciente_nome")
        if isinstance(paciente_id, int) and isinstance(nome, str) and nome.strip():
            pacientes[paciente_id] = nome.strip()

    formulario = st.empty()
    with formulario.container(key="modal-nova-evolucao", border=True):
        titulo, fechar = st.columns([1, 0.12], vertical_alignment="center")
        fechar.button("×", key="nova-evolucao-fechar", help="Fechar nova evolução",
                      on_click=_limpar_formulario)
        with titulo:
            st.subheader("Nova evolução clínica")
            st.caption("Este Registro Clínico fará parte do Prontuário do Paciente.")

        if not pacientes:
            st.info("Não há Pacientes no escopo das Consultas deste Profissional.")
            return

        paciente_ids = list(pacientes)
        if st.session_state.get("nova-evolucao-paciente") not in paciente_ids:
            _trocar_paciente()
            selecionado = st.session_state.get("prontuario_paciente_id")
            st.session_state["nova-evolucao-paciente"] = (
                selecionado if selecionado in paciente_ids else paciente_ids[0]
            )
        paciente_id = st.selectbox(
            "Paciente", paciente_ids,
            format_func=lambda item: pacientes[item],
            key="nova-evolucao-paciente", on_change=_trocar_paciente,
        )
        consultas_paciente = _consultas_paciente(consultas, paciente_id)
        consulta_ids = [None] + [item["id"] for item in consultas_paciente]
        if st.session_state.get("nova-evolucao-consulta") not in consulta_ids:
            st.session_state.pop("nova-evolucao-consulta", None)
        with st.form("nova-evolucao-form", clear_on_submit=False):
            consulta_id = st.selectbox(
                "Consulta relacionada (opcional)", consulta_ids,
                format_func=lambda selecionada: "Sem Consulta" if selecionada is None else next(
                    f"{consulta['inicio_em']} · {consulta['situacao']}"
                    for consulta in consultas_paciente if consulta["id"] == selecionada
                ),
                key="nova-evolucao-consulta",
            )
            st.caption(f"Profissional responsável: {conta.nome} · autoria definida pela sua Conta de Acesso")
            conteudo = st.text_area(
                "Evolução e observações", max_chars=8000,
                placeholder="Descreva o atendimento, achados clínicos, orientações e próximos passos",
                key="nova-evolucao-conteudo",
            )
            cancelar, acao = st.columns(2)
            salvar = acao.form_submit_button("Salvar no prontuário", key="nova-evolucao-salvar", type="primary", width="stretch")
            cancelar.form_submit_button("Cancelar", key="nova-evolucao-cancelar", on_click=_limpar_formulario, width="stretch")

        if salvar:
            if not conteudo or not conteudo.strip():
                st.error("Informe a evolução clínica antes de salvar.")
                return
            try:
                with st.spinner("Salvando no Prontuário…"):
                    cliente.registrar_clinico(
                        credencial.token, paciente_id, conteudo,
                        consulta_id=consulta_id,
                    )
            except ErroAcesso as error:
                if error.status == 401:
                    sessao.limpar(st.session_state)
                    formulario.error("Sua sessão expirou. Entre novamente.")
                elif error.status == 403:
                    st.error("Sua Conta de Acesso não tem permissão para registrar esta evolução.")
                elif error.status == 404:
                    st.error("Paciente ou Consulta não encontrados no escopo permitido.")
                else:
                    st.error("Não foi possível confirmar o Registro Clínico. Atualize o histórico antes de tentar novamente.")
                return
            except Exception:
                st.error("Não foi possível confirmar o Registro Clínico. Atualize o histórico antes de tentar novamente.")
                return

            invalidar_cache(st.session_state, ("registros-clinicos", "prontuario"))
            st.session_state.pop(_CHAVE_CACHE, None)
            _limpar_formulario()
            st.session_state["prontuario_aviso"] = "Registro Clínico salvo no Prontuário."
            st.rerun()
