"""Listagem conectada de Profissionais ativos."""

import hashlib
import time

import streamlit as st

from .api import ErroAcesso
from . import sessao

_CHAVE_CACHE_PROFISSIONAIS = "profissionais_xano_cache"
_TTL_CACHE_SEGUNDOS = 20


def _iniciais(nome):
    partes = nome.split()
    return "".join(parte[0] for parte in partes[:2]).upper() or "P"


def _listar_profissionais(cliente, token, estado, atualizar=False):
    """Reutiliza por 20 segundos a lista bem-sucedida da sessão atual."""
    identidade_token = hashlib.sha256(token.encode("utf-8")).hexdigest()
    cache = estado.get(_CHAVE_CACHE_PROFISSIONAIS)
    agora = time.monotonic()

    if cache and cache[0] != identidade_token:
        estado.pop(_CHAVE_CACHE_PROFISSIONAIS, None)
        cache = None

    if (not atualizar and cache and 0 <= agora - cache[1] < _TTL_CACHE_SEGUNDOS):
        return cache[2]

    # Resultados expirados e resultados explicitamente atualizados não podem
    # reaparecer se a consulta falhar.
    estado.pop(_CHAVE_CACHE_PROFISSIONAIS, None)
    opcoes = cliente.listar_opcoes_agenda(token)
    profissionais = [dict(item) for item in opcoes["profissionais"]]
    estado[_CHAVE_CACHE_PROFISSIONAIS] = (
        identidade_token, time.monotonic(), profissionais,
    )
    return profissionais


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
        st.session_state.pop(_CHAVE_CACHE_PROFISSIONAIS, None)
        st.error("Sua sessão expirou. Entre novamente para consultar os Profissionais.")
        return

    atualizar = st.button("Atualizar lista", key="profissionais-xano-atualizar")
    try:
        if atualizar or _CHAVE_CACHE_PROFISSIONAIS not in st.session_state:
            with st.spinner("Carregando Profissionais…"):
                profissionais = _listar_profissionais(
                    cliente, credencial.token, st.session_state, atualizar=atualizar,
                )
        else:
            profissionais = _listar_profissionais(
                cliente, credencial.token, st.session_state,
            )
    except ErroAcesso as error:
        if error.status == 401:
            st.session_state.pop(_CHAVE_CACHE_PROFISSIONAIS, None)
            sessao.limpar(st.session_state)
        st.error(str(error))
        return

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
