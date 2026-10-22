"""Tela isolada para agendamento conectado de Consulta."""
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

import streamlit as st

from .api import ErroAcesso
from . import sessao

FUSO_CLINICA = ZoneInfo("America/Sao_Paulo")


def _limites_data(dia):
    """Retorna limites ISO 8601 locais para consultar a agenda do dia."""
    inicio = datetime.combine(dia, time.min, tzinfo=FUSO_CLINICA)
    fim = inicio + timedelta(days=1)
    return inicio.isoformat(timespec="seconds"), fim.isoformat(timespec="seconds")


def _horario_legivel(disponibilidade):
    inicio = datetime.fromisoformat(disponibilidade["inicio"].replace("Z", "+00:00"))
    fim = datetime.fromisoformat(disponibilidade["fim"].replace("Z", "+00:00"))
    inicio = inicio.astimezone(FUSO_CLINICA)
    fim = fim.astimezone(FUSO_CLINICA)
    return f"{inicio:%H:%M} – {fim:%H:%M}"


def _perfis(conta):
    return {perfil.casefold() for perfil in getattr(conta, "perfis", ())}


def renderizar(cliente, conta):
    """Renderiza Nova Consulta usando exclusivamente os contratos Xano existentes."""
    if not _perfis(conta).intersection({"administrador", "recepcionista"}):
        st.title("Nova consulta")
        st.error("Seu perfil não tem permissão para agendar consultas.")
        return

    if st.session_state.pop("nova_consulta_concluida", False):
        for chave in (
            "nova-consulta-paciente", "nova-consulta-data",
            "nova-consulta-profissional", "nova-consulta-horario",
            "nova-consulta-procedimentos", "nova-consulta-observacao",
        ):
            st.session_state.pop(chave, None)
        st.success("Consulta agendada.")

    st.title("Nova consulta")
    st.caption("Escolha o Paciente, o Profissional e um horário disponível.")
    credencial = st.session_state.get(sessao.CHAVE)
    token = getattr(credencial, "token", None)
    if not token:
        st.error("Sua sessão expirou. Entre novamente para continuar.")
        return

    try:
        opcoes = cliente.listar_opcoes_agenda(token)
    except ErroAcesso as error:
        st.error(str(error) if error.status in (401, 403, 429)
                 else "Não foi possível carregar as opções de agendamento. Tente novamente.")
        return

    pacientes = {item["id"]: item["nome"] for item in opcoes.get("pacientes", [])}
    profissionais = {item["id"]: item["nome"] for item in opcoes.get("profissionais", [])}
    procedimentos = {item["id"]: item["nome"] for item in opcoes.get("procedimentos", [])}
    if not pacientes or not profissionais:
        st.info("Cadastre Pacientes e Profissionais ativos antes de agendar.")
        return

    st.subheader("Dados da consulta")
    paciente_id = st.selectbox(
        "Paciente", list(pacientes), format_func=pacientes.get,
        index=None, placeholder="Selecione um Paciente",
        key="nova-consulta-paciente",
    )
    data_consulta = st.date_input("Data", value=date.today(), format="DD/MM/YYYY",
                                  key="nova-consulta-data")
    profissional_id = st.selectbox("Profissional", list(profissionais),
                                   format_func=profissionais.get,
                                   key="nova-consulta-profissional")

    inicio, fim = _limites_data(data_consulta)
    try:
        disponibilidades = cliente.listar_disponibilidades(
            token, profissional_id, inicio, fim
        )
    except ErroAcesso as error:
        st.error(str(error) if error.status in (401, 403, 429)
                 else "Não foi possível carregar os horários disponíveis.")
        return

    disponibilidades = [item for item in disponibilidades
                        if item.get("situacao") == "disponivel"]
    horarios = {item["id"]: _horario_legivel(item) for item in disponibilidades}
    if not horarios:
        st.info("Nenhum horário disponível para este Profissional nesta data.")

    with st.form("nova-consulta-form"):
        disponibilidade_id = st.selectbox(
            "Horário", list(horarios), format_func=horarios.get,
            index=None, placeholder="Selecione um horário", disabled=not horarios,
            key="nova-consulta-horario",
        )
        procedimento_ids = st.multiselect(
            "Procedimentos (opcional)", list(procedimentos),
            format_func=procedimentos.get, key="nova-consulta-procedimentos",
        )
        observacao = st.text_area(
            "Observação administrativa (opcional)", max_chars=1000,
            placeholder="Informações administrativas para a consulta",
            key="nova-consulta-observacao",
        )
        cancelar, agendar = st.columns(2)
        cancelar_envio = cancelar.form_submit_button("Cancelar", width="stretch")
        enviar = agendar.form_submit_button(
            "Agendar consulta", type="primary", disabled=not horarios,
            width="stretch",
        )

    if cancelar_envio:
        st.session_state["pagina_equipe"] = "agenda"
        return
    if not enviar:
        return
    if paciente_id is None:
        st.error("Selecione um Paciente.")
        return
    if disponibilidade_id is None:
        st.error("Selecione um horário disponível.")
        return
    try:
        cliente.agendar_consulta(
            token, paciente_id, disponibilidade_id, procedimento_ids,
            motivo=observacao.strip() or None,
        )
    except ErroAcesso as error:
        st.error(str(error))
        return

    st.session_state["nova_consulta_concluida"] = True
    st.rerun()
