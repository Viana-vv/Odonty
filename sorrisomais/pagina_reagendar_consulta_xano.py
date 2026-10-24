"""Tela administrativa de reagendamento conectado de Consulta."""

from datetime import datetime

import streamlit as st

from . import sessao
from .api import ErroAcesso
from .pagina_nova_consulta_xano import (
    FUSO_CLINICA, _horario_legivel, _leitura_com_cache,
    _limites_data, _limpar_cache_leituras, _perfis,
)
from .reagendamento_consulta import reagendar_consulta

PREFIXO = "reagendar-consulta-"


def _limpar_selecoes():
    for chave in list(st.session_state):
        if chave.startswith(PREFIXO):
            st.session_state.pop(chave, None)
    _limpar_cache_leituras()


def _erro(error):
    if error.status == 401:
        sessao.limpar(st.session_state)
    _limpar_cache_leituras()
    if error.status == 409:
        st.error("A Consulta ou o horário mudou. Atualize a seleção e tente novamente.")
    elif error.status in (400, 401, 403, 404, 429):
        st.error(str(error))
    else:
        st.error("Não foi possível concluir o reagendamento. Tente novamente.")


def _consulta_legivel(consulta):
    inicio = datetime.fromisoformat(consulta["inicio_em"].replace("Z", "+00:00"))
    inicio = inicio.astimezone(FUSO_CLINICA)
    return (f"{inicio:%d/%m/%Y às %H:%M} · "
            f"{consulta.get('profissional_nome', 'Profissional')} · {consulta['situacao']}")


def _selecionar(label, opcoes, sufixo, **kwargs):
    chave = PREFIXO + sufixo
    if st.session_state.get(chave) not in opcoes:
        st.session_state.pop(chave, None)
    return st.selectbox(label, list(opcoes), key=chave, **kwargs)


def _formulario(cliente, token, opcoes):
    pacientes = {item["id"]: item["nome"] for item in opcoes.get("pacientes", [])}
    profissionais = {item["id"]: item["nome"] for item in opcoes.get("profissionais", [])}
    if not pacientes or not profissionais:
        st.info("Cadastre Pacientes e Profissionais ativos antes de reagendar.")
        return

    st.caption("1. Consulta original")
    paciente_id = _selecionar(
        "Paciente", pacientes, "paciente", format_func=pacientes.get,
        index=None, placeholder="Selecione um Paciente",
    )
    if paciente_id is None:
        return
    if st.session_state.get(PREFIXO + "paciente-anterior") != paciente_id:
        for campo in ("consulta", "profissional", "data", "horario", "filtro-horarios"):
            st.session_state.pop(PREFIXO + campo, None)
        st.session_state[PREFIXO + "paciente-anterior"] = paciente_id

    consultas = _leitura_com_cache(
        token, ("reagendamento-consultas", paciente_id),
        lambda: cliente.listar_consultas(token, paciente_id=paciente_id),
    )
    # GET pode repetir uma Consulta por Procedimento; o seletor usa seu ID único.
    consultas = {item["id"]: item for item in consultas
                 if item.get("situacao") in {"Agendada", "Confirmada"}
                 and item.get("disponibilidade_id") is not None}
    if not consultas:
        st.info("Nenhuma Consulta Agendada ou Confirmada com horário vinculado para este Paciente.")
        return
    consulta_id = _selecionar(
        "Consulta original", consultas, "consulta", index=None,
        placeholder="Selecione uma Consulta",
        format_func=lambda identificador: _consulta_legivel(consultas[identificador]),
    )
    if consulta_id is None:
        return
    consulta = consultas[consulta_id]
    if st.session_state.get(PREFIXO + "consulta-anterior") != consulta_id:
        for campo in ("profissional", "data", "horario", "filtro-horarios", "justificativa"):
            st.session_state.pop(PREFIXO + campo, None)
        st.session_state[PREFIXO + "consulta-anterior"] = consulta_id

    st.caption("2. Novo horário")
    data_coluna, profissional_coluna = st.columns(2, gap="medium")
    with data_coluna:
        dia = st.date_input(
            "Data", value=datetime.now(FUSO_CLINICA).date(), format="DD/MM/YYYY",
            key=PREFIXO + "data",
        )
    with profissional_coluna:
        profissional_id = _selecionar(
            "Profissional", profissionais, "profissional",
            index=(list(profissionais).index(consulta["profissional_id"])
                   if consulta["profissional_id"] in profissionais else 0),
            format_func=profissionais.get,
        )
    filtro = (consulta_id, profissional_id, dia)
    if st.session_state.get(PREFIXO + "filtro-horarios") != filtro:
        st.session_state.pop(PREFIXO + "horario", None)
        st.session_state[PREFIXO + "filtro-horarios"] = filtro
    inicio, fim = _limites_data(dia)
    disponibilidades = _leitura_com_cache(
        token, ("reagendamento-disponibilidades", profissional_id, inicio, fim),
        lambda: cliente.listar_disponibilidades(token, profissional_id, inicio, fim),
    )
    horarios = {item["id"]: _horario_legivel(item) for item in disponibilidades
                if item.get("situacao") == "disponivel"
                and item["id"] != consulta["disponibilidade_id"]}
    if not horarios:
        st.info("Nenhum horário disponível para este Profissional nesta data.")
    with st.form(PREFIXO + "form", border=False):
        disponibilidade_id = _selecionar(
            "Horário", horarios, "horario", index=None,
            format_func=horarios.get, placeholder="Selecione um horário",
            disabled=not horarios,
        )
        justificativa = st.text_area(
            "Justificativa do reagendamento", max_chars=1000,
            placeholder="Informe o motivo administrativo da mudança",
            key=PREFIXO + "justificativa",
        )
        cancelar, confirmar = st.columns(2, gap="small")
        voltar = cancelar.form_submit_button("Cancelar", width="stretch")
        enviar = confirmar.form_submit_button(
            "Reagendar consulta", type="primary", width="stretch", disabled=not horarios,
        )
    if voltar:
        st.session_state["pagina_equipe"] = "agenda"
        return
    if not enviar:
        return
    if disponibilidade_id is None:
        st.error("Selecione um horário disponível.")
        return
    if not justificativa.strip():
        st.error("Informe a justificativa do reagendamento.")
        return
    reagendar_consulta(cliente, token, consulta_id, disponibilidade_id, justificativa)
    _limpar_cache_leituras()
    st.session_state["reagendamento_concluido"] = True
    st.rerun()


def renderizar(cliente, conta):
    """Renderiza a ação administrativa; a autorização efetiva permanece no Xano."""
    titulo, atualizar = st.columns([3, 1], vertical_alignment="center")
    titulo.subheader("Reagendar consulta")
    titulo.caption("Selecione a Consulta original e escolha um novo horário.")
    if not _perfis(conta).intersection({"administrador", "recepcionista"}):
        st.error("Seu perfil não tem permissão para reagendar Consultas.")
        return
    if st.session_state.pop("reagendamento_concluido", False):
        _limpar_selecoes()
        st.success("Consulta reagendada. A Consulta original foi preservada no histórico.")
    atualizar.button("Atualizar", key=PREFIXO + "atualizar", on_click=_limpar_selecoes)
    token = getattr(st.session_state.get(sessao.CHAVE), "token", None)
    if not token:
        st.error("Sua sessão expirou. Entre novamente para continuar.")
        return
    try:
        opcoes = _leitura_com_cache(
            token, ("agenda/opcoes",), lambda: cliente.listar_opcoes_agenda(token),
        )
        with st.container(key="formulario-reagendar-consulta", border=True):
            _formulario(cliente, token, opcoes)
    except ErroAcesso as error:
        _erro(error)
