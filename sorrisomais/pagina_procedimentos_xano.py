"""Catálogo de Procedimentos conectado, somente para leitura."""

from hashlib import sha256
from time import monotonic

import streamlit as st

from . import sessao
from .api import ErroAcesso


_CACHE_CHAVE = "procedimentos_xano_catalogo_cache"
_FALHA_CHAVE = "procedimentos_xano_catalogo_falha"
_CACHE_TTL_SEGUNDOS = 20


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

    if "administrador" not in set(getattr(conta, "perfis", ())):
        st.info("Seu perfil não tem acesso ao catálogo de Procedimentos.")
        return

    credencial = st.session_state.get(sessao.CHAVE)
    token = getattr(credencial, "token", None)
    if not isinstance(token, str) or not token or any(caractere.isspace() for caractere in token):
        st.info("Sua sessão expirou. Entre novamente para acessar o catálogo de Procedimentos.")
        return

    identificador_token = sha256(token.encode("utf-8")).hexdigest()
    cache = st.session_state.get(_CACHE_CHAVE)
    if cache is not None and (
        not isinstance(cache, dict) or cache.get("token") != identificador_token
    ):
        st.session_state.pop(_CACHE_CHAVE, None)
        cache = None
    if cache is not None and monotonic() - cache.get("carregado_em", 0) >= _CACHE_TTL_SEGUNDOS:
        st.session_state.pop(_CACHE_CHAVE, None)
        cache = None
    if st.session_state.get(_FALHA_CHAVE) != identificador_token:
        st.session_state.pop(_FALHA_CHAVE, None)

    busca = st.text_input("Buscar Procedimento", key="procedimentos_xano_busca").strip()
    falha = st.session_state.get(_FALHA_CHAVE)
    if falha == identificador_token:
        st.error("Não foi possível carregar os Procedimentos. Tente novamente.")
        if st.button("Tentar novamente", key="procedimentos_xano_recarregar"):
            st.session_state.pop(_FALHA_CHAVE, None)
            st.rerun()
        return

    if cache is None:
        try:
            with st.spinner("Carregando Procedimentos…"):
                opcoes = cliente.listar_opcoes_agenda(token)
            procedimentos = opcoes["procedimentos"]
        except ErroAcesso as error:
            if error.status in (401, 403):
                st.session_state.pop(_CACHE_CHAVE, None)
                st.session_state.pop(_FALHA_CHAVE, None)
                sessao.limpar(st.session_state)
                st.error(str(error))
                return
            st.session_state[_FALHA_CHAVE] = identificador_token
            st.error("Não foi possível carregar os Procedimentos. Tente novamente.")
            if st.button("Tentar novamente", key="procedimentos_xano_recarregar"):
                st.session_state.pop(_FALHA_CHAVE, None)
                st.rerun()
            return
        except (KeyError, TypeError, ValueError):
            st.session_state[_FALHA_CHAVE] = identificador_token
            st.error("Não foi possível carregar os Procedimentos. Tente novamente.")
            if st.button("Tentar novamente", key="procedimentos_xano_recarregar"):
                st.session_state.pop(_FALHA_CHAVE, None)
                st.rerun()
            return
        st.session_state[_CACHE_CHAVE] = {
            "token": identificador_token,
            "carregado_em": monotonic(),
            "procedimentos": procedimentos,
        }
    else:
        procedimentos = cache["procedimentos"]

    if st.session_state.get(_CACHE_CHAVE) is not None and st.button(
        "Atualizar catálogo", key="procedimentos_xano_atualizar"
    ):
        st.session_state.pop(_CACHE_CHAVE, None)
        st.rerun()

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
