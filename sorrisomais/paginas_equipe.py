"""Páginas da equipe. A identidade é revalidada por app.py antes de renderizar."""
import streamlit as st
from pathlib import Path

from .api import ErroAcesso, ROTULOS
from . import sessao, pagina_paciente


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


def abrir_inicio():
    limpar_formulario()
    pagina_paciente.limpar()
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
    restaurar = st.session_state.pop("cad_restaurar", {})
    for campo, valor in restaurar.items():
        st.session_state["cad_" + campo] = valor
    if st.session_state.pop("cad_limpar", False):
        limpar_formulario()
        st.success("Profissional cadastrado. Ele já pode entrar pelo login da equipe.")
    st.caption("EQUIPE DA CLÍNICA")
    st.title("Novo profissional")
    st.markdown("Cadastre o Dentista e associe uma especialidade ativa.")
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
                if dados:
                    st.session_state["cad_restaurar"] = {
                        "nome": dados["nome"], "email": dados["email"],
                        "cro": dados["cro"], "especialidade": dados["especialidade_id"],
                    }
        finally:
            if dados:
                dados.clear()
            if sessao.CHAVE in st.session_state:
                st.session_state["cad_processando"] = False
        st.rerun()


def renderizar_inicio(conta, administrador, pode_cadastrar_paciente):
    st.caption("VISÃO GERAL")
    st.header(f"Olá, {conta.nome}!")
    st.write("Aqui está seu espaço para cuidar da rotina da clínica.")
    rotulos = ("Dentista" if perfil == "profissional" else ROTULOS[perfil]
               for perfil in conta.perfis)
    st.text(" · ".join(rotulos))

    col_acoes, col_mascote = st.columns([1.55, 1], gap="large", vertical_alignment="top")
    with col_acoes:
        with st.container(key="cartao-acesso", border=True):
            st.subheader("Acesso rápido")
            st.caption("Abra uma das ações disponíveis para o seu perfil.")
            if pode_cadastrar_paciente:
                st.button("Cadastrar paciente", on_click=pagina_paciente.abrir,
                          key="inicio-cadastrar-paciente", type="primary", width="stretch")
            if administrador:
                st.button("Cadastrar profissional", on_click=abrir_cadastro,
                          key="inicio-cadastrar-profissional", width="stretch")
            if not administrador and not pode_cadastrar_paciente:
                st.info("Seu acesso à equipe está ativo.")
    with col_mascote:
        with st.container(key="cartao-mascote", border=True):
            mascote = Path(__file__).resolve().parents[1] / "assets" / "mascote-sorriso.png"
            st.image(str(mascote), caption="Sorriso+", width=190)
            st.caption("Cuidar começa com uma boa organização.")


def renderizar(conta, cliente):
    administrador = "administrador" in conta.perfis
    pode_cadastrar_paciente = (cliente.configuracao.cadastro_paciente_habilitado
                              and bool(set(conta.perfis) & {"administrador", "recepcionista"}))
    if not administrador:
        limpar_formulario()
        if st.session_state.get("pagina_equipe") == "cadastro":
            st.session_state.pop("pagina_equipe", None)
    if not pode_cadastrar_paciente:
        pagina_paciente.limpar()
        if st.session_state.get("pagina_equipe") == "paciente":
            st.session_state.pop("pagina_equipe", None)
    pagina = st.session_state.get("pagina_equipe", "inicio")
    ocupado = (st.session_state.get("cad_processando", False)
               or st.session_state.get("pac_processando", False))
    with st.container(key="layout-equipe"):
        menu, conteudo = st.columns([0.24, 0.76], gap="medium", vertical_alignment="top")
        with menu:
            with st.container(key="menu-equipe", border=True):
                st.markdown("### Sorriso+")
                st.caption("EQUIPE DA CLÍNICA")
                st.button("Visão geral", on_click=abrir_inicio, key="menu-inicio",
                          disabled=ocupado, width="stretch")
                if pode_cadastrar_paciente:
                    st.button("Cadastrar paciente", on_click=pagina_paciente.abrir,
                              key="menu-cadastrar-paciente", disabled=ocupado or pagina == "paciente",
                              width="stretch")
                if administrador:
                    st.button("Cadastrar profissional", on_click=abrir_cadastro,
                              key="menu-cadastrar-profissional", disabled=ocupado or pagina == "cadastro",
                              width="stretch")
                st.divider()
                st.caption("SEU ACESSO")
                st.text(conta.nome)
                st.caption(" · ".join(ROTULOS[p] for p in conta.perfis))
                if st.button("Sair", key="sair", width="stretch", disabled=ocupado):
                    with st.spinner("Encerrando seu acesso…"):
                        mensagem = sessao.sair(st.session_state, cliente)
                    st.session_state["aviso"] = ("info", mensagem)
                    st.rerun()
        with conteudo:
            with st.container(key="conteudo-equipe", border=True):
                if administrador and pagina == "cadastro":
                    with st.container(key="formulario-equipe"):
                        renderizar_cadastro(cliente)
                elif pode_cadastrar_paciente and pagina == "paciente":
                    with st.container(key="formulario-equipe"):
                        pagina_paciente.renderizar(cliente)
                else:
                    renderizar_inicio(conta, administrador, pode_cadastrar_paciente)
