"""Tela isolada para agendamento conectado de Consulta."""
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

import streamlit as st

from .api import ErroAcesso
from . import sessao

FUSO_CLINICA = ZoneInfo("America/Sao_Paulo")
def _limpar_cache_leituras():
    st.session_state.pop("nova-consulta-cache-leituras", None)
    from .cache_xano import invalidar_cache
    invalidar_cache(st.session_state)


def _normalizar_namespace_cache(chave):
    partes = tuple(chave)
    recurso = str(partes[0])
    parametros = partes[1:]
    if recurso in {"agenda/opcoes", "exames-solicitacao-opcoes"}:
        return "agenda/opcoes"
    if recurso in {"consultas", "exames-solicitacao-consultas"}:
        namespace = "consultas"
        if parametros:
            namespace += f":paciente={parametros[0]}"
        return namespace
    if recurso in {"reagendamento-consultas", "consultas:paciente"}:
        return f"consultas:paciente={parametros[0]}"
    if "disponibilidades" in recurso:
        profissional, inicio, fim = parametros
        return f"disponibilidades:profissional={profissional}:inicio={inicio}:fim={fim}"
    if parametros:
        return recurso + ":" + ":".join(str(parte) for parte in parametros)
    return recurso


def _leitura_com_cache(token, chave, carregar, *, force=False):
    """Normaliza o namespace e delega ao cache privado central."""
    from .cache_xano import carregar_cache
    return carregar_cache(
        st.session_state, token, _normalizar_namespace_cache(chave), carregar, force=force
    )


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


def _exibir_erro_api(error, mensagem_generica):
    if error.status == 401:
        sessao.limpar(st.session_state)
        _limpar_cache_leituras()
    elif error.status in (403, 409):
        # Permissões ou horários podem mudar depois que a lista foi carregada.
        _limpar_cache_leituras()
    if error.status in (401, 403, 409, 429):
        st.error(str(error))
    else:
        st.error(mensagem_generica)


def _renderizar_formulario(cliente, token, pacientes, profissionais, procedimentos):
    titulo, atualizar = st.columns([3, 1], vertical_alignment="center")
    titulo.subheader("Nova consulta")
    titulo.caption("Escolha o Paciente, o Profissional e um horário.")
    atualizar.button(
        "Atualizar", key="nova-consulta-atualizar",
        help="Recarregar Pacientes, Profissionais, Procedimentos e horários.",
        on_click=_limpar_cache_leituras,
    )
    st.caption("1. Dados da consulta")
    paciente_id = st.selectbox(
        "Paciente", list(pacientes), format_func=pacientes.get,
        index=None, placeholder="Selecione um Paciente",
        key="nova-consulta-paciente",
    )

    data_coluna, profissional_coluna = st.columns(2, gap="medium")
    data_consulta = data_coluna.date_input(
        "Data", value=st.session_state.get(
            "agenda_data_input",
            st.session_state.get("agenda_data", datetime.now(FUSO_CLINICA).date()),
        ),
        format="DD/MM/YYYY",
        key="nova-consulta-data",
    )
    profissional_id = profissional_coluna.selectbox(
        "Profissional", list(profissionais), format_func=profissionais.get,
        key="nova-consulta-profissional",
    )

    st.caption("2. Horário e procedimento")

    filtro_horarios = (profissional_id, data_consulta)
    if st.session_state.get("nova-consulta-filtro-horarios") != filtro_horarios:
        st.session_state.pop("nova-consulta-horario", None)
        st.session_state["nova-consulta-filtro-horarios"] = filtro_horarios

    inicio, fim = _limites_data(data_consulta)
    try:
        disponibilidades = _leitura_com_cache(
            token,
            ("disponibilidades", profissional_id, inicio, fim),
            lambda: cliente.listar_disponibilidades(
                token, profissional_id, inicio, fim
            ),
        )
    except ErroAcesso as error:
        _exibir_erro_api(error, "Não foi possível carregar os horários disponíveis.")
        return

    disponibilidades = [item for item in disponibilidades
                        if item.get("situacao") == "disponivel"]
    horarios = {item["id"]: _horario_legivel(item) for item in disponibilidades}
    if not horarios:
        st.info("Nenhum horário disponível para este Profissional nesta data.")

    horario_coluna, procedimento_coluna = st.columns(2, gap="medium")
    with st.form("nova-consulta-form", border=False):
        disponibilidade_id = horario_coluna.selectbox(
            "Horário", list(horarios), format_func=horarios.get,
            index=None, placeholder="Selecione um horário", disabled=not horarios,
            key="nova-consulta-horario",
        )
        procedimento_ids = procedimento_coluna.multiselect(
            "Procedimentos (opcional)", list(procedimentos),
            format_func=procedimentos.get, placeholder="Selecione",
            key="nova-consulta-procedimentos",
        )
        observacao = st.text_area(
            "Observações (opcional)", max_chars=1000,
            placeholder="Informações administrativas para a consulta",
            key="nova-consulta-observacao",
        )
        cancelar, agendar = st.columns(2, gap="small")
        cancelar_envio = cancelar.form_submit_button("Cancelar", width="stretch")
        enviar = agendar.form_submit_button(
            "Agendar consulta", type="primary", disabled=not horarios,
            width="stretch",
        )

    if cancelar_envio:
        st.session_state["pagina_equipe"] = "agenda"
        st.rerun()
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
        _exibir_erro_api(error, "Não foi possível agendar a Consulta. Tente novamente.")
        return

    st.session_state["nova_consulta_concluida"] = True
    st.rerun()


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
            "nova-consulta-filtro-horarios",
        ):
            st.session_state.pop(chave, None)
        _limpar_cache_leituras()
        st.success("Consulta agendada.")

    credencial = st.session_state.get(sessao.CHAVE)
    token = getattr(credencial, "token", None)
    if not token:
        st.error("Sua sessão expirou. Entre novamente para continuar.")
        return

    try:
        opcoes = _leitura_com_cache(
            token,
            ("agenda/opcoes",),
            lambda: cliente.listar_opcoes_agenda(token),
        )
    except ErroAcesso as error:
        _exibir_erro_api(
            error, "Não foi possível carregar as opções de agendamento. Tente novamente."
        )
        return

    pacientes = {item["id"]: item["nome"] for item in opcoes.get("pacientes", [])}
    profissionais = {item["id"]: item["nome"] for item in opcoes.get("profissionais", [])}
    procedimentos = {item["id"]: item["nome"] for item in opcoes.get("procedimentos", [])}
    if not pacientes or not profissionais:
        st.info("Cadastre Pacientes e Profissionais ativos antes de agendar.")
        return

    with st.container(key="formulario-nova-consulta", border=True):
        _renderizar_formulario(cliente, token, pacientes, profissionais, procedimentos)
