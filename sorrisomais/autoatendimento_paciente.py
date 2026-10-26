"""Renderização do portal pessoal do Paciente."""

from datetime import datetime
from zoneinfo import ZoneInfo

import streamlit as st

from .api import ErroAcesso
from .exames_api import ClienteExames
from .pagina_consultas_paciente import renderizar as renderizar_consultas
from . import sessao_paciente

FUSO_CLINICA = ZoneInfo("America/Sao_Paulo")


def _data_hora(valor):
    if not isinstance(valor, str):
        return "Data não informada"
    try:
        instante = datetime.fromisoformat(valor.replace("Z", "+00:00"))
        if instante.tzinfo is None:
            instante = instante.replace(tzinfo=FUSO_CLINICA)
        return instante.astimezone(FUSO_CLINICA).strftime("%d/%m/%Y às %H:%M")
    except ValueError:
        return "Data não informada"


def _mensagem_erro(erro):
    if erro.status in (401, 403):
        sessao_paciente.limpar(st.session_state)
        st.error("Sua sessão expirou ou não tem permissão. Entre novamente.")
        st.rerun()
    st.error("Não foi possível carregar estas informações. Tente novamente mais tarde.")


def _renderizar_consultas(cliente, token):
    renderizar_consultas(cliente, token)


def _renderizar_registros(cliente, token):
    st.subheader("Informações liberadas pela clínica")
    try:
        registros = cliente.listar_registros_clinicos(token)
    except ErroAcesso as erro:
        _mensagem_erro(erro)
        return
    liberados = [r for r in registros if r.get("liberado_paciente") is True]
    if not liberados:
        st.info("A clínica ainda não liberou informações para consulta.")
        return
    for registro in liberados:
        with st.container(border=True):
            st.caption(_data_hora(registro.get("registrado_em")))
            st.write(registro.get("conteudo", ""))
            nome = registro.get("profissional_nome") or f"Profissional #{registro.get('profissional_id', 'não informado')}"
            st.caption(f"Profissional: {nome}")


def _renderizar_exames(cliente, token):
    st.subheader("Meus Exames")
    st.caption("Resultados são exibidos depois que a clínica os libera.")
    try:
        exames = ClienteExames(cliente).listar(token)
    except ErroAcesso as erro:
        _mensagem_erro(erro)
        return
    if not exames:
        st.info("Você não possui Exames disponíveis para consulta.")
        return
    for exame in exames:
        with st.container(border=True):
            st.markdown(f"**{exame.get('tipo', 'Exame')}**")
            st.write(f"Situação: {exame.get('situacao', 'Não informada')}")
            st.caption(f"Solicitado em {_data_hora(exame.get('solicitado_em'))}")
            if exame.get("realizado_em"):
                st.caption(f"Realizado em {_data_hora(exame['realizado_em'])}")
            resultado = exame.get("resultado")
            if exame.get("situacao") == "Resultado disponível" and isinstance(resultado, str) and resultado:
                st.markdown("**Resultado liberado**")
                st.write(resultado)


def solicitar_entrada():
    if st.session_state.get("paciente_processando"):
        return
    st.session_state["paciente_entrada_pendente"] = (
        st.session_state.get("paciente_email", ""), st.session_state.get("paciente_senha", "")
    )
    st.session_state["paciente_email"] = ""
    st.session_state["paciente_senha"] = ""
    st.session_state["paciente_processando"] = True

def renderizar(cliente):
    conta = sessao_paciente.identificar(st.session_state, cliente)
    if conta is None:
        st.caption("SORRISO MAIS · ÁREA DO PACIENTE")
        st.title("Acompanhe seu atendimento")
        st.markdown("Entre para consultar suas Consultas e as informações liberadas pela clínica.")
        aviso = st.session_state.pop("paciente_aviso", None)
        if aviso:
            st.error(aviso)
        with st.form("paciente-login"):
            st.text_input("E-mail", key="paciente_email", autocomplete="email")
            st.text_input("Senha", key="paciente_senha", type="password", autocomplete="current-password")
            st.form_submit_button("Entrar", type="primary", width="stretch", on_click=solicitar_entrada)
        if st.session_state.pop("paciente_processando", False):
            email, senha = st.session_state.pop("paciente_entrada_pendente", ("", ""))
            try:
                with st.spinner("Verificando seu acesso…"):
                    sessao_paciente.entrar(st.session_state, cliente, email, senha)
            except ErroAcesso as erro:
                st.session_state["paciente_aviso"] = str(erro)
            finally:
                senha = None
            st.rerun()
        st.caption("Acesso pessoal do Paciente. A equipe utiliza outro endereço.")
        return

    st.caption("SORRISO MAIS · ÁREA DO PACIENTE")
    st.title(f"Olá, {conta.nome}")
    if st.button("Sair", key="paciente-sair"):
        st.session_state["paciente_aviso_saida"] = sessao_paciente.sair(st.session_state, cliente)
        st.rerun()
    aviso_saida = st.session_state.pop("paciente_aviso_saida", None)
    if aviso_saida:
        st.info(aviso_saida)
    token = st.session_state[sessao_paciente.CHAVE_CREDENCIAL].token
    consultas_tab, registros_tab, exames_tab = st.tabs(["Consultas", "Informações liberadas", "Exames"])
    with consultas_tab:
        _renderizar_consultas(cliente, token)
    with registros_tab:
        _renderizar_registros(cliente, token)
    with exames_tab:
        _renderizar_exames(cliente, token)
