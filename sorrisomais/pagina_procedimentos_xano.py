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

    with st.container(key="catalogo-procedimentos", border=True):
        for procedimento in encontrados:
            with st.container(key=f"procedimento-xano-{procedimento['id']}"):
                simbolo, nome = st.columns([.4, 6], vertical_alignment="center")
                simbolo.markdown('<span class="icone-procedimento"><svg viewBox="0 0 32 32" width="30" height="30" fill="none" stroke="currentColor" stroke-width="2.4"><path d="M16 6C11 2 4 5 5 12c1 5 2 14 5 15 3 1 2-10 6-10s3 11 6 10c3-1 4-10 5-15 1-7-6-10-11-6Z"/></svg></span>', unsafe_allow_html=True)
                nome.markdown(f"**{procedimento['nome']}**")
