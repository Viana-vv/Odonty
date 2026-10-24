"""Consulta das Consultas próprias pelo Paciente."""

from datetime import datetime
from zoneinfo import ZoneInfo

import streamlit as st

from .api import ErroAcesso

FUSO_CLINICA = ZoneInfo("America/Sao_Paulo")


def _inicio_consulta(consulta):
    try:
        inicio = datetime.fromisoformat(consulta["inicio_em"])
        if inicio.tzinfo is None:
            inicio = inicio.replace(tzinfo=FUSO_CLINICA)
        return inicio.astimezone(FUSO_CLINICA)
    except (KeyError, TypeError, ValueError):
        return None


def _cartao(consulta, inicio, *, futura):
    dia = inicio.strftime("%d/%m/%Y")
    hora = inicio.strftime("%H:%M")
    st.markdown(f"**{dia} às {hora}** · {consulta['profissional_nome']}  \nSituação: {consulta['situacao']}")
    if futura:
        st.caption("Para solicitar o cancelamento, entre em contato com a clínica.")


def renderizar(cliente, token):
    st.title("Minhas Consultas")
    st.markdown("Acompanhe suas Consultas futuras e passadas.")
    try:
        consultas = cliente.listar_consultas(token)
    except ErroAcesso as erro:
        if erro.status in (401, 403):
            st.error("Não foi possível acessar suas Consultas. Entre novamente ou contate a clínica.")
        else:
            st.error("Não foi possível carregar suas Consultas. Tente novamente mais tarde.")
        return

    agora = datetime.now(FUSO_CLINICA)
    itens = [(consulta, _inicio_consulta(consulta)) for consulta in consultas]
    itens = [(consulta, inicio) for consulta, inicio in itens if inicio is not None]
    aba = st.radio("Período", ("Futuras", "Passadas"), horizontal=True,
                   label_visibility="collapsed", key="consultas-paciente-periodo")
    futuras = aba == "Futuras"
    filtradas = [(consulta, inicio) for consulta, inicio in itens
                 if (inicio >= agora) == futuras]
    filtradas.sort(key=lambda item: item[1], reverse=not futuras)
    st.subheader("Consultas futuras" if futuras else "Consultas passadas")
    if not filtradas:
        st.info("Você não possui Consultas neste período.")
        return
    for consulta, inicio in filtradas:
        with st.container(border=True):
            _cartao(consulta, inicio, futura=futuras)
