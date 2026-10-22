"""Listagem conectada de Profissionais ativos."""

import streamlit as st

from .api import ErroAcesso
from . import sessao


def _iniciais(nome):
    partes = nome.split()
    return "".join(parte[0] for parte in partes[:2]).upper() or "P"


def renderizar(cliente, conta):
    """Exibe os Profissionais ativos fornecidos pelo Xano."""
    st.caption("EQUIPE DA CLÍNICA")
    st.title("Profissionais")
    st.write("Consulte os Profissionais ativos da clínica.")

    if not set(conta.perfis).intersection({"administrador", "recepcionista"}):
        st.info("Seu perfil não tem permissão para consultar esta lista.")
        return

    credencial = st.session_state.get(sessao.CHAVE)
    if credencial is None:
        st.error("Sua sessão expirou. Entre novamente para consultar os Profissionais.")
        return

    try:
        with st.spinner("Carregando Profissionais…"):
            opcoes = cliente.listar_opcoes_agenda(credencial.token)
    except ErroAcesso as error:
        if error.status == 401:
            sessao.limpar(st.session_state)
        st.error(str(error))
        return

    profissionais = opcoes["profissionais"]
    if not profissionais:
        st.info("Não há Profissionais ativos para exibir.")
        return

    colunas = st.columns(3, gap="medium")
    for indice, profissional in enumerate(profissionais):
        coluna = colunas[indice % len(colunas)]
        with coluna:
            with st.container(border=True, key=f"profissional-xano-{profissional['id']}"):
                avatar, situacao = st.columns([1, 1], vertical_alignment="center")
                avatar.markdown(f"### {_iniciais(profissional['nome'])}")
                situacao.caption("● Ativo")
                st.subheader(profissional["nome"])
