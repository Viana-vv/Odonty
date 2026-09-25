"""Páginas da equipe. A identidade é revalidada por app.py antes de renderizar."""
import streamlit as st

from .api import ErroAcesso, ROTULOS
from . import sessao


def limpar_formulario():
    for chave in list(st.session_state):
        if chave.startswith("cad_"):
            del st.session_state[chave]


def abrir_cadastro():
    limpar_formulario()
    st.session_state["pagina_equipe"] = "cadastro"


def voltar():
    limpar_formulario()
    st.session_state["pagina_equipe"] = "inicio"


def solicitar_cadastro():
    if st.session_state.get("cad_processando"):
        return
    senha = st.session_state.get("cad_senha", "")
    confirmacao = st.session_state.get("cad_confirmacao", "")
    st.session_state["cad_senha"] = ""
    st.session_state["cad_confirmacao"] = ""
    if senha != confirmacao:
        st.session_state["cad_aviso"] = ("error", "A confirmação da senha não confere.")
        return
    st.session_state["cad_pendente"] = {
        "nome": st.session_state.get("cad_nome", ""),
        "email": st.session_state.get("cad_email", ""),
        "senha": senha,
        "cro": st.session_state.get("cad_cro", ""),
        "especialidade_id": st.session_state.get("cad_especialidade"),
    }
    st.session_state["cad_processando"] = True


def renderizar_cadastro(cliente):
    if st.session_state.pop("cad_limpar", False):
        limpar_formulario()
        st.success("Profissional cadastrado. Ele já pode entrar pelo login da equipe.")
    st.title("Cadastrar profissional")
    st.caption("CADASTRO DA EQUIPE")
    st.button("Voltar", key="voltar", on_click=voltar,
              disabled=st.session_state.get("cad_processando", False))
    token = st.session_state[sessao.CHAVE].token
    try:
        especialidades = cliente.listar_especialidades(token)
    except ErroAcesso as error:
        limpar_formulario()
        if error.status in (401, 403):
            sessao.limpar(st.session_state)
            st.session_state["aviso"] = ("error", str(error))
            st.rerun()
        st.error("Não foi possível carregar as especialidades. Tente novamente em instantes.")
        st.button("Tentar novamente", on_click=limpar_formulario)
        return
    opcoes = {item["id"]: item["nome"] for item in especialidades}
    if not opcoes:
        st.info("Nenhuma especialidade disponível. Configure uma especialidade ativa no Xano.")
    ocupado = st.session_state.get("cad_processando", False)
    mensagem = st.session_state.pop("cad_aviso", None)
    if mensagem:
        getattr(st, mensagem[0])(mensagem[1])
    with st.form("cadastro_profissional", border=True):
        st.text_input("Nome completo", key="cad_nome", max_chars=120, disabled=ocupado)
        st.text_input("E-mail do profissional", key="cad_email", max_chars=254, disabled=ocupado)
        st.text_input("Senha inicial", key="cad_senha", type="password", max_chars=128,
                      help="De 12 a 128 caracteres.", disabled=ocupado)
        st.text_input("Confirmar senha", key="cad_confirmacao", type="password",
                      max_chars=128, disabled=ocupado)
        st.markdown("**Perfil de acesso: Dentista**")
        st.text_input("CRO", key="cad_cro", placeholder="SP-123456", max_chars=32, disabled=ocupado)
        st.selectbox("Especialidade", options=list(opcoes), index=None,
                     format_func=lambda value: opcoes.get(value, ""),
                     placeholder="Selecione a especialidade", key="cad_especialidade",
                     disabled=ocupado or not opcoes)
        st.form_submit_button("Cadastrando…" if ocupado else "Cadastrar",
                              type="primary", width="stretch",
                              on_click=solicitar_cadastro, disabled=ocupado or not opcoes)
    if ocupado:
        dados = st.session_state.pop("cad_pendente", None)
        try:
            if dados:
                with st.spinner("Cadastrando profissional…"):
                    cliente.cadastrar_profissional(token, **dados)
                st.session_state["cad_limpar"] = True
        except ErroAcesso as error:
            if error.status in (401, 403):
                sessao.limpar(st.session_state)
                st.session_state["aviso"] = ("error", str(error))
            else:
                st.session_state["cad_aviso"] = ("error", str(error))
        finally:
            if dados:
                dados.clear()
            if sessao.CHAVE in st.session_state:
                st.session_state["cad_processando"] = False
        st.rerun()


def renderizar(conta, cliente):
    administrador = "administrador" in conta.perfis
    if not administrador:
        limpar_formulario()
        st.session_state.pop("pagina_equipe", None)
    with st.container(key="acesso", border=True):
        st.caption("SEU ACESSO")
        if administrador and st.session_state.get("pagina_equipe") == "cadastro":
            renderizar_cadastro(cliente)
        else:
            st.title("Página do Administrador" if administrador else "Bem-vindo ao Sorriso+")
            st.text(conta.nome)
            st.text(" · ".join(ROTULOS[p] for p in conta.perfis))
            if administrador:
                st.button("Cadastrar profissional", type="primary",
                          on_click=abrir_cadastro, width="stretch")
        if st.button("Sair", key="sair", width="stretch",
                     disabled=st.session_state.get("cad_processando", False)):
            with st.spinner("Encerrando seu acesso…"):
                mensagem = sessao.sair(st.session_state, cliente)
            st.session_state["aviso"] = ("info", mensagem)
            st.rerun()
