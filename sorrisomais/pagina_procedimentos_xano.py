"""Gestão do catálogo de Procedimentos conectado ao Xano."""

import streamlit as st

from . import sessao
from .api import ErroAcesso
from .cache_xano import carregar_cache
from .icones import icone_html


def _filtrar_procedimentos(procedimentos, busca, filtro):
    termo = busca.strip().casefold()
    resultado = []
    for item in procedimentos:
        if not isinstance(item, dict) or not isinstance(item.get("nome"), str):
            continue
        ativo = item.get("ativo", True)
        if filtro == "Ativos" and not ativo:
            continue
        if filtro == "Inativos" and ativo:
            continue
        if termo and termo not in item["nome"].casefold():
            continue
        resultado.append(item)
    return resultado


@st.dialog("Novo Procedimento")
def _modal_novo(cliente, token):
    st.caption("Cadastre um Procedimento para uso nas Consultas.")
    nome = st.text_input("Nome do Procedimento", key="modal-procedimento-nome")
    salvar, fechar = st.columns(2)
    if fechar.button("Cancelar", key="modal-procedimento-cancelar"):
        st.rerun()
    if salvar.button("Salvar no Xano", key="modal-procedimento-salvar", type="primary"):
        try:
            cliente.criar_procedimento(token, nome)
            st.session_state["procedimentos_feedback"] = "Procedimento salvo no Xano."
            st.session_state.pop("xano_get_cache", None)
            st.rerun()
        except ErroAcesso as error:
            st.error(str(error))


@st.dialog("Editar Procedimento")
def _modal_editar(cliente, token, procedimento):
    st.caption("Atualize o nome ou a situação do Procedimento.")
    nome = st.text_input("Nome do Procedimento", value=procedimento["nome"],
                         key=f"modal-procedimento-editar-nome-{procedimento['id']}")
    ativo = procedimento.get("ativo", True)
    st.info(f"Situação atual: {'Ativo' if ativo else 'Inativo'}")
    salvar, alternar = st.columns(2)
    if salvar.button("Salvar edição", key=f"modal-procedimento-editar-salvar-{procedimento['id']}", type="primary"):
        try:
            cliente.atualizar_procedimento(token, procedimento["id"], nome=nome)
            st.session_state["procedimentos_feedback"] = "Procedimento atualizado."
            st.session_state.pop("xano_get_cache", None)
            st.rerun()
        except ErroAcesso as error:
            st.error(str(error))
    acao = "Inativar Procedimento" if ativo else "Ativar Procedimento"
    if alternar.button(acao, key=f"modal-procedimento-editar-situacao-{procedimento['id']}"):
        try:
            cliente.atualizar_procedimento(token, procedimento["id"], ativo=not ativo)
            st.session_state["procedimentos_feedback"] = (
                "Procedimento inativado." if ativo else "Procedimento ativado."
            )
            st.session_state.pop("xano_get_cache", None)
            st.rerun()
        except ErroAcesso as error:
            st.error(str(error))


def renderizar(cliente, conta):
    st.title("Procedimentos")
    st.caption("Catálogo compartilhado da clínica")
    perfis = set(getattr(conta, "perfis", ()))
    pode_criar = bool(perfis.intersection({"administrador", "recepcionista", "profissional"}))
    pode_gerenciar = bool(perfis.intersection({"administrador", "recepcionista"}))
    if not pode_criar:
        st.info("Seu perfil não tem acesso aos Procedimentos.")
        return

    credencial = st.session_state.get(sessao.CHAVE)
    token = getattr(credencial, "token", None)
    if not isinstance(token, str) or not token or any(caractere.isspace() for caractere in token):
        st.info("Sua sessão expirou. Entre novamente para acessar os Procedimentos.")
        return

    feedback = st.session_state.pop("procedimentos_feedback", None)
    if feedback:
        st.success(feedback)

    acao, resumo = st.columns([1, 3], vertical_alignment="center")
    if acao.button("Novo Procedimento", key="procedimentos-abrir-novo", type="primary"):
        _modal_novo(cliente, token)
    resumo.caption("Crie Procedimentos pelo modal. Administradores e Recepcionistas também podem editar ou inativar.")

    filtros = st.columns([2, 1, 1], gap="small", vertical_alignment="bottom")
    busca = filtros[0].text_input("Buscar", placeholder="Nome do Procedimento", key="procedimentos_xano_busca")
    filtro = filtros[1].selectbox("Situação", ["Ativos", "Todos", "Inativos"], key="procedimentos_xano_filtro")
    atualizar = filtros[2].button("Atualizar", key="procedimentos_xano_atualizar", width="stretch")
    try:
        procedimentos = carregar_cache(
            st.session_state, token, "procedimentos",
            lambda: cliente.listar_procedimentos(token), force=atualizar,
        )
    except ErroAcesso as error:
        if error.status in (401, 403):
            sessao.limpar(st.session_state)
        st.error(str(error) if error.status in (401, 403) else "Não foi possível carregar os Procedimentos.")
        return

    encontrados = _filtrar_procedimentos(procedimentos, busca, filtro)
    if not encontrados:
        st.info("Nenhum Procedimento encontrado para os filtros selecionados.")
        return

    st.caption(f"{len(encontrados)} Procedimento(s)")
    for procedimento in encontrados:
        ativo = procedimento.get("ativo", True)
        with st.container(key=f"procedimento-card-{procedimento['id']}", border=True):
            icone, conteudo, acao_edicao = st.columns([0.5, 4, 1.2], vertical_alignment="center")
            icone.markdown(icone_html("tool"), unsafe_allow_html=True)
            conteudo.markdown(f"**{procedimento['nome']}**")
            conteudo.caption("Ativo · disponível para novas Consultas" if ativo else "Inativo · mantido no histórico")
            if pode_gerenciar and acao_edicao.button("Gerenciar", key=f"procedimento-gerenciar-{procedimento['id']}"):
                _modal_editar(cliente, token, procedimento)
