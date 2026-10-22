"""Listagem conectada de Pacientes com dados administrativos mínimos."""

import streamlit as st

from . import sessao
from .api import ErroAcesso


def renderizar(cliente, conta):
    """Renderiza a listagem usando exclusivamente as opções da Agenda no Xano."""
    st.caption("BASE DE PACIENTES")
    st.title("Pacientes")
    st.markdown("Consulte os cadastros disponíveis para a equipe.")

    credencial = st.session_state.get(sessao.CHAVE)
    if not credencial:
        st.info("Sua sessão expirou. Entre novamente para consultar os Pacientes.")
        return

    try:
        with st.spinner("Carregando pacientes…"):
            opcoes = cliente.listar_opcoes_agenda(credencial.token)
    except ErroAcesso as error:
        if error.status in (401, 403):
            st.error("Sua Conta de Acesso não tem permissão para consultar os Pacientes.")
        else:
            st.error(str(error))
        return

    pacientes = opcoes["pacientes"]
    if not pacientes:
        st.info("Nenhum Paciente disponível para exibição.")
        return

    coluna_busca, coluna_total = st.columns([5, 1], vertical_alignment="center")
    with coluna_busca:
        termo = st.text_input(
            "Buscar por nome",
            placeholder="Digite o nome do Paciente...",
            key="pacientes-xano-busca",
            label_visibility="collapsed",
        ).strip().casefold()

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
