"""Cadastro administrativo de Paciente, sem criação de credenciais."""

from datetime import date
from uuid import uuid4

import streamlit as st

from . import sessao
from .api import ErroAcesso
from .pacientes import hoje, validar_cadastro


def limpar():
    for chave in list(st.session_state):
        if chave.startswith("pac_"):
            del st.session_state[chave]


def abrir():
    limpar()
    st.session_state["pagina_equipe"] = "paciente"


def voltar():
    limpar()
    st.session_state["pagina_equipe"] = "inicio"


def solicitar():
    if st.session_state.get("pac_processando") or st.session_state.get("pac_pendente"):
        return
    nascimento = st.session_state.get("pac_data_nascimento")
    try:
        dados = validar_cadastro(
            st.session_state.get("pac_nome"),
            nascimento.isoformat() if isinstance(nascimento, date) else None,
            st.session_state.get("pac_telefone"), st.session_state.get("pac_cpf"),
            st.session_state.get("pac_email"), st.session_state.get("pac_celular"),
        )
    except ErroAcesso as error:
        st.session_state["pac_aviso"] = str(error)
        return
    dados["operacao_id"] = st.session_state.setdefault("pac_operacao_id", str(uuid4()))
    st.session_state["pac_pendente"] = dados
    st.session_state["pac_processando"] = True


def reenviar():
    if st.session_state.get("pac_pendente") and not st.session_state.get("pac_processando"):
        st.session_state["pac_processando"] = True


def renderizar(cliente):
    if st.session_state.pop("pac_sucesso", False):
        limpar()
        st.success("Paciente cadastrado com prontuário vazio. Este cadastro não cria login.")
    restaurar = st.session_state.pop("pac_restaurar", {})
    for campo, valor in restaurar.items():
        st.session_state["pac_" + campo] = valor
    st.session_state.setdefault("pac_operacao_id", str(uuid4()))
    st.caption("Preencha os dados cadastrais para criar um Paciente com prontuário vazio.")
    ocupado = st.session_state.get("pac_processando", False)
    pendente = st.session_state.get("pac_pendente")
    aviso = st.session_state.pop("pac_aviso", None)
    if aviso:
        st.error(aviso)
    if pendente:
        st.warning("Há uma operação sem confirmação. Os dados estão preservados. "
                   "Voltar ou sair não desfaz um cadastro que possa ter sido concluído. "
                   "Se sair, confira o resultado com o responsável antes de abrir outro cadastro.")
        bloqueado = st.session_state.get("pac_conflitante", False)
        st.button("Reenviar mesma operação", on_click=reenviar, disabled=ocupado or bloqueado)
    with st.form("cadastro_paciente", border=False):
        bloqueado = ocupado or bool(pendente)
        st.text_input("Nome completo *", key="pac_nome", max_chars=120,
                      placeholder="Ex.: Maria de Souza", disabled=bloqueado)
        cpf, nascimento = st.columns(2, gap="medium")
        cpf.text_input("CPF *", key="pac_cpf", max_chars=14,
                       placeholder="000.000.000-00", disabled=bloqueado)
        nascimento.date_input("Data de nascimento *", key="pac_data_nascimento", value=None,
                              min_value=date.min, max_value=hoje(), format="DD/MM/YYYY", disabled=bloqueado)
        telefone, email = st.columns(2, gap="medium")
        telefone.text_input("Telefone *", key="pac_telefone", max_chars=15, placeholder="(00) 00000-0000",
                            disabled=bloqueado)
        email.text_input("E-mail *", key="pac_email", max_chars=254,
                         placeholder="paciente@email.com", disabled=bloqueado)
        st.text_input("Celular *", key="pac_celular", max_chars=15, placeholder="(00) 00000-0000",
                      disabled=bloqueado)
        cancelar, enviar = st.columns([1, 1.3], gap="small", vertical_alignment="center")
        cancelar.form_submit_button("Cancelar", on_click=voltar, disabled=ocupado, width="stretch")
        enviar.form_submit_button("Cadastrando…" if ocupado else "Cadastrar paciente", type="primary",
                                  on_click=solicitar, disabled=bloqueado or ocupado, width="stretch")
    if ocupado and pendente:
        dados = dict(pendente)
        campos = {campo: dados[campo] or "" for campo in ("nome", "telefone", "cpf", "email", "celular")}
        campos["data_nascimento"] = date.fromisoformat(dados["data_nascimento"])
        try:
            with st.spinner("Cadastrando paciente…"):
                cliente.cadastrar_paciente(st.session_state[sessao.CHAVE].token, **dados)
            st.session_state["pac_sucesso"] = True
        except ErroAcesso as error:
            if error.status in (401, 403):
                sessao.limpar(st.session_state)
                st.session_state["aviso"] = ("error", str(error))
            else:
                st.session_state["pac_aviso"] = str(error)
                st.session_state["pac_restaurar"] = campos
                if error.status == 400 or error.codigo == "CPF_DUPLICADO":
                    st.session_state.pop("pac_pendente", None)
                    st.session_state["pac_operacao_id"] = str(uuid4())
                elif error.codigo == "OPERACAO_CONFLITANTE":
                    st.session_state["pac_conflitante"] = True
        finally:
            if sessao.CHAVE in st.session_state:
                st.session_state["pac_processando"] = False
        st.rerun()


def renderizar_modal(cliente):
    with st.container(key="modal-paciente"):
        cabecalho, fechar = st.columns([8, 1], vertical_alignment="center")
        cabecalho.markdown("### Novo paciente")
        if fechar.button("×", key="pac-fechar-modal", help="Fechar cadastro"):
            voltar()
            st.rerun()
        st.divider()
        renderizar(cliente)
