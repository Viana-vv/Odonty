"""Catálogo de Procedimentos conectado, somente para leitura."""

import streamlit as st

from . import sessao
from .api import ErroAcesso


def _filtrar_procedimentos(procedimentos, busca):
    termo = busca.strip().casefold()
    if not termo:
        return procedimentos
    return [item for item in procedimentos if termo in item["nome"].casefold()]


def renderizar(cliente, conta):
    """Exibe os Procedimentos autorizados pelo Xano sem dados adicionais."""
    st.title("Procedimentos")
    st.caption("Catálogo da clínica")
    st.write("Consulte os Procedimentos disponíveis.")

    if not set(getattr(conta, "perfis", ())).intersection({"administrador", "recepcionista"}):
        st.info("Seu perfil não tem acesso ao catálogo de Procedimentos.")
        return

    busca = st.text_input("Buscar Procedimento", key="procedimentos_xano_busca").strip()
    token = st.session_state[sessao.CHAVE].token
    try:
        with st.spinner("Carregando Procedimentos…"):
            opcoes = cliente.listar_opcoes_agenda(token)
        procedimentos = opcoes["procedimentos"]
    except (ErroAcesso, KeyError, TypeError, ValueError):
        st.error("Não foi possível carregar os Procedimentos. Tente novamente.")
        if st.button("Tentar novamente", key="procedimentos_xano_recarregar"):
            st.rerun()
        return

    encontrados = _filtrar_procedimentos(procedimentos, busca)
    if not encontrados:
        if procedimentos:
            st.info("Nenhum Procedimento corresponde à busca.")
        else:
            st.info("Nenhum Procedimento disponível no momento.")
        return

    colunas = st.columns(2, gap="medium")
    for indice, procedimento in enumerate(encontrados):
        with colunas[indice % 2]:
            with st.container(key=f"procedimento-xano-{procedimento['id']}", border=True):
                st.markdown(f"◇  **{procedimento['nome']}**")
