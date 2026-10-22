"""Listagem conectada de Pacientes com dados administrativos mínimos."""

import hashlib
from time import monotonic

import streamlit as st

from . import sessao
from .api import ErroAcesso

CACHE_PACIENTES = "pacientes_xano_cache"
CACHE_TTL_SEGUNDOS = 20


def _carregar_pacientes(cliente, credencial, atualizar=False):
    """Mantém a resposta somente nesta sessão; falhas nunca entram no cache."""
    identificador_sessao = hashlib.sha256(credencial.token.encode("utf-8")).hexdigest()
    cache = st.session_state.get(CACHE_PACIENTES)
    idade_cache = (monotonic() - cache.get("carregado_em", 0)
                   if isinstance(cache, dict) else CACHE_TTL_SEGUNDOS)
    if (not atualizar and isinstance(cache, dict)
            and cache.get("sessao") == identificador_sessao
            and 0 <= idade_cache < CACHE_TTL_SEGUNDOS
            and isinstance(cache.get("pacientes"), list)):
        return cache["pacientes"]

    if atualizar:
        st.session_state.pop(CACHE_PACIENTES, None)
    opcoes = cliente.listar_opcoes_agenda(credencial.token)
    pacientes = opcoes["pacientes"]
    st.session_state[CACHE_PACIENTES] = {
        "sessao": identificador_sessao,
        "pacientes": pacientes,
        "carregado_em": monotonic(),
    }
    return pacientes


def renderizar(cliente, conta):
    """Renderiza a listagem usando exclusivamente as opções da Agenda no Xano."""
    st.caption("BASE DE PACIENTES")
    st.title("Pacientes")
    st.markdown("Consulte os cadastros disponíveis para a equipe.")

    credencial = st.session_state.get(sessao.CHAVE)
    if not credencial:
        st.info("Sua sessão expirou. Entre novamente para consultar os Pacientes.")
        return

    coluna_busca, coluna_atualizar, coluna_total = st.columns([5, 1, 1], vertical_alignment="center")
    with coluna_busca:
        termo = st.text_input(
            "Buscar por nome",
            placeholder="Digite o nome do Paciente...",
            key="pacientes-xano-busca",
            label_visibility="collapsed",
        ).strip().casefold()
    atualizar = coluna_atualizar.button("Atualizar", key="pacientes-xano-atualizar")

    try:
        with st.spinner("Carregando pacientes…"):
            pacientes = _carregar_pacientes(cliente, credencial, atualizar=atualizar)
    except ErroAcesso as error:
        if error.status in (401, 403):
            if error.status == 401:
                sessao.limpar(st.session_state)
                st.error("Sua sessão expirou. Entre novamente para consultar os Pacientes.")
            else:
                st.session_state.pop(CACHE_PACIENTES, None)
                st.error("Sua Conta de Acesso não tem permissão para consultar os Pacientes.")
        else:
            st.error(str(error))
        return

    if not pacientes:
        st.info("Nenhum Paciente disponível para exibição.")
        return

    filtrados = [paciente for paciente in pacientes
                 if termo in paciente["nome"].casefold()]
    with coluna_total:
        st.caption(f"{len(filtrados)} pacientes")

    if not filtrados:
        st.info("Nenhum Paciente corresponde à busca.")
        return

    with st.container(key="pacientes-xano-tabela", border=True):
        identificador, nome = st.columns([1, 5])
        identificador.caption("ID")
        nome.caption("Paciente")
        for paciente in filtrados:
            with st.container(key=f"pacientes-xano-linha-{paciente['id']}"):
                identificador, nome = st.columns([1, 5], vertical_alignment="center")
                identificador.text(str(paciente["id"]))
                nome.markdown(f"**{paciente['nome']}**")
                st.divider()
