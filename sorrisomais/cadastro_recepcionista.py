"""Cadastro administrativo de uma Conta de Acesso de Recepcionista."""

import streamlit as st

from . import sessao
from .api import ErroAcesso
from .cache_xano import invalidar_cache

NOME = "recepcao_cadastro_nome"
EMAIL = "recepcao_cadastro_email"
SENHA = "recepcao_cadastro_senha"
CONFIRMACAO = "recepcao_cadastro_confirmacao"
AVISO = "recepcao_cadastro_aviso"
PROCESSANDO = "recepcao_cadastro_processando"
ABERTO = "recepcao_cadastro_aberto"
SUCESSO = "recepcao_cadastro_sucesso"


def limpar():
    for chave in (ABERTO, NOME, EMAIL, SENHA, CONFIRMACAO, AVISO, PROCESSANDO):
        st.session_state.pop(chave, None)


def abrir():
    st.session_state[ABERTO] = True


def _enviar(cliente):
    estado = st.session_state
    if not estado.get(ABERTO) or estado.get(PROCESSANDO) or estado.get(SUCESSO):
        return
    senha, confirmacao = estado.get(SENHA, ""), estado.get(CONFIRMACAO, "")
    estado[SENHA] = estado[CONFIRMACAO] = ""
    if senha != confirmacao:
        estado[AVISO] = "A confirmação da senha não confere."
        return
    credencial = estado.get(sessao.CHAVE)
    if not credencial:
        estado[AVISO] = "Sua sessão expirou. Entre novamente para continuar."
        return

    estado[PROCESSANDO] = True
    try:
        cliente.cadastrar_recepcionista(
            credencial.token, estado.get(NOME, ""), estado.get(EMAIL, ""), senha,
        )
    except ErroAcesso as erro:
        estado[AVISO] = str(erro)
    else:
        invalidar_cache(estado, namespaces="contas-acesso")
        estado[SUCESSO] = True
    finally:
        estado.pop(PROCESSANDO, None)


@st.dialog("Cadastrar recepcionista", on_dismiss=limpar)
def _modal(cliente):
    if st.session_state.get(SUCESSO):
        limpar()
        st.rerun()
    st.caption("Perfil da nova Conta de Acesso: Recepcionista")
    aviso = st.session_state.pop(AVISO, None)
    if aviso:
        st.error(aviso)
    with st.form("cadastro_recepcionista", border=False):
        st.text_input("Nome completo", key=NOME, max_chars=120)
        st.text_input("E-mail", key=EMAIL, max_chars=254)
        st.text_input("Senha inicial", key=SENHA, type="password", max_chars=128,
                      help="De 12 a 128 caracteres.")
        st.text_input("Confirmar senha", key=CONFIRMACAO, type="password", max_chars=128)
        st.form_submit_button("Cadastrar recepcionista", type="primary", width="stretch",
                              on_click=_enviar, args=(cliente,),
                              disabled=st.session_state.get(PROCESSANDO, False))


def renderizar(cliente, conta):
    if "administrador" in conta.perfis and st.session_state.get(ABERTO):
        _modal(cliente)
