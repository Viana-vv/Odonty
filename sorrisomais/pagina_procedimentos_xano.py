"""Catálogo de Procedimentos conectado, somente para leitura."""


import streamlit as st

from . import sessao
from .api import ErroAcesso
from .cache_xano import carregar_cache



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

    busca = st.text_input("Buscar Procedimento", key="procedimentos_xano_busca").strip()
    atualizar = st.button("Atualizar cat\u00e1logo", key="procedimentos_xano_atualizar")
    try:
        opcoes = carregar_cache(st.session_state, token, "agenda/opcoes", lambda: cliente.listar_opcoes_agenda(token), force=atualizar)
        procedimentos = opcoes["procedimentos"]
    except ErroAcesso as error:
        if error.status in (401, 403):
            sessao.limpar(st.session_state)
        st.error(str(error) if error.status in (401, 403) else "N\u00e3o foi poss\u00edvel carregar os Procedimentos. Tente novamente.")
        if error.status not in (401, 403) and st.button("Tentar novamente", key="procedimentos_xano_recarregar"):
            st.rerun()
        return
    except (KeyError, TypeError, ValueError):
        st.error("N\u00e3o foi poss\u00edvel carregar os Procedimentos. Tente novamente.")
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
