"""Listagem conectada de Pacientes com dados administrativos mínimos."""

import hashlib
from datetime import date

import streamlit as st

from . import sessao
from .api import ErroAcesso
from . import cache_xano
from . import pagina_paciente

CHAVE_EDICAO = "pacientes_xano_edicao"
PREFIXO_FORMULARIO = "pacientes_xano_edicao_"
CHAVE_MENSAGEM = "pacientes_xano_mensagem"


def _carregar_pacientes(cliente, credencial, atualizar=False):
    """Carrega a lista no cache privado da sessão autenticada."""
    opcoes = cache_xano.carregar_cache(
        st.session_state,
        credencial.token,
        "agenda/opcoes",
        lambda: cliente.listar_opcoes_agenda(credencial.token),
        force=atualizar,
    )
    return opcoes["pacientes"]


def _limpar_edicao():
    st.session_state.pop(CHAVE_EDICAO, None)
    for chave in list(st.session_state):
        if chave.startswith(PREFIXO_FORMULARIO):
            st.session_state.pop(chave, None)


def _mensagem_edicao(error):
    if error.status == 400:
        return "Confira os dados cadastrais informados e tente novamente."
    if error.status == 404:
        return "Este Paciente não foi encontrado. Atualize a listagem e tente novamente."
    if error.status == 409:
        return "O CPF informado já está cadastrado. Confira os dados e tente novamente."
    if error.status == 429:
        return "Muitas tentativas. Aguarde um pouco antes de tentar novamente."
    return "Não foi possível concluir a edição. Tente novamente em instantes."


def _iniciais(nome):
    partes = nome.split()
    return "".join(parte[0] for parte in partes[:2]).upper() or "P"


@st.dialog("Editar Paciente", width="large")
def _renderizar_edicao(cliente, credencial, edicao):
    paciente = edicao["paciente"]
    with st.container(key="pacientes-xano-edicao"):
        st.caption("Altere os dados cadastrais. Informações clínicas não são exibidas nesta tela.")
        with st.form("pacientes-xano-form-edicao", border=False):
            nome = st.text_input("Nome completo *", value=paciente["nome"], max_chars=120,
                                 key=f"{PREFIXO_FORMULARIO}nome")
            col_cpf, col_nascimento = st.columns(2)
            cpf = col_cpf.text_input("CPF *", value=paciente["cpf"], max_chars=14,
                                     key=f"{PREFIXO_FORMULARIO}cpf")
            nascimento = col_nascimento.date_input(
                "Data de nascimento *", value=date.fromisoformat(paciente["data_nascimento"]),
                min_value=date(1900, 1, 1), max_value=date.today(), format="DD/MM/YYYY",
                key=f"{PREFIXO_FORMULARIO}nascimento",
            )
            col_telefone, col_celular = st.columns(2)
            telefone = col_telefone.text_input("Telefone *", value=paciente["telefone"],
                                                key=f"{PREFIXO_FORMULARIO}telefone")
            celular = col_celular.text_input("Celular *", value=paciente["celular"],
                                             key=f"{PREFIXO_FORMULARIO}celular")
            email = st.text_input("E-mail *", value=paciente["email"], max_chars=254,
                                  key=f"{PREFIXO_FORMULARIO}email")
            col_cancelar, col_salvar = st.columns([1, 1])
            cancelar = col_cancelar.form_submit_button("Cancelar", width="stretch")
            salvar = col_salvar.form_submit_button("Salvar alterações", type="primary", width="stretch")

    if cancelar:
        _limpar_edicao()
        st.rerun()
    if salvar:
        try:
            cliente.atualizar_paciente(
                credencial.token, paciente["id"], nome=nome,
                data_nascimento=nascimento.isoformat(), telefone=telefone,
                cpf=cpf, email=email, celular=celular,
            )
            _limpar_edicao()
            cache_xano.invalidar_cache(
                st.session_state,
                namespaces=["pacientes", "agenda/opcoes", f"paciente:{paciente['id']}"],
            )
            st.session_state[CHAVE_MENSAGEM] = "Os dados cadastrais do Paciente foram atualizados."
            st.rerun()
        except ErroAcesso as error:
            if error.status == 401:
                sessao.limpar(st.session_state)
                st.error("Sua sessão expirou. Entre novamente para editar o Paciente.")
            elif error.status == 403:
                st.error("Sua Conta de Acesso não tem permissão para editar Pacientes.")
            else:
                st.error(_mensagem_edicao(error))


def renderizar(cliente, conta):
    """Renderiza a listagem usando exclusivamente as opções da Agenda no Xano."""
    st.caption("BASE DE PACIENTES")
    st.title("Pacientes")
    st.markdown("Consulte os dados cadastrais dos Pacientes.")

    mensagem = st.session_state.pop(CHAVE_MENSAGEM, None)
    if mensagem:
        st.success(mensagem)

    credencial = st.session_state.get(sessao.CHAVE)
    if not credencial:
        _limpar_edicao()
        st.info("Sua sessão expirou. Entre novamente para consultar os Pacientes.")
        return

    identificador_sessao = hashlib.sha256(credencial.token.encode("utf-8")).hexdigest()
    perfis = set(getattr(conta, "perfis", ()))
    pode_editar = bool(perfis.intersection({"administrador", "recepcionista"}))
    if not pode_editar:
        _limpar_edicao()
    edicao = st.session_state.get(CHAVE_EDICAO)
    if isinstance(edicao, dict) and edicao.get("sessao") != identificador_sessao:
        _limpar_edicao()
        edicao = None

    cabecalho, acao_cadastro = st.columns([5, 1], vertical_alignment="center")
    with acao_cadastro:
        if pode_editar and st.button("＋ Novo Paciente", type="primary", key="pacientes-xano-novo"):
            pagina_paciente.abrir()
            st.rerun()

    coluna_busca, coluna_atualizar, coluna_total = st.columns([5, 1, 1], vertical_alignment="center")
    with coluna_busca:
        termo = st.text_input(
            "Buscar Paciente",
            placeholder="Buscar por nome...",
            key="pacientes-xano-busca",
            label_visibility="collapsed",
        ).strip().casefold()
    atualizar = coluna_atualizar.button("Atualizar", key="pacientes-xano-atualizar")

    try:
        with st.spinner("Carregando pacientes…"):
            pacientes = _carregar_pacientes(cliente, credencial, atualizar=atualizar)
    except ErroAcesso as error:
        if error.status in (401, 403):
            if error.status == 401:
                sessao.limpar(st.session_state)
                st.error("Sua sessão expirou. Entre novamente para consultar os Pacientes.")
            else:
                cache_xano.invalidar_cache(st.session_state, namespaces=["pacientes", "agenda/opcoes"])
                _limpar_edicao()
                st.error("Sua Conta de Acesso não tem permissão para consultar os Pacientes.")
        else:
            st.error(str(error))
        return

    if not pacientes:
        st.info("Nenhum Paciente disponível para exibição.")
        return

    filtrados = [paciente for paciente in pacientes
                 if termo in paciente["nome"].casefold()]
    with coluna_total:
        st.caption(f"{len(filtrados)} pacientes")

    if not filtrados:
        st.info("Nenhum Paciente corresponde à busca.")
        return

    with st.container(key="pacientes-xano-tabela", border=True):
        identificador, paciente_coluna, acao = st.columns([1, 6, 1])
        identificador.caption("ID")
        paciente_coluna.caption("Paciente")
        acao.caption("Ações")
        for paciente in filtrados:
            with st.container(key=f"pacientes-xano-linha-{paciente['id']}"):
                identificador, detalhes, acao = st.columns([1, 6, 1], vertical_alignment="center")
                identificador.text(str(paciente["id"]))
                avatar, nome = detalhes.columns([1, 10], vertical_alignment="center")
                avatar.markdown(
                    f'<div class="paciente-avatar">{_iniciais(paciente["nome"])}</div>',
                    unsafe_allow_html=True,
                )
                nome.markdown(f"**{paciente['nome']}**")
                if pode_editar and acao.button("Editar", key=f"pacientes-xano-editar-{paciente['id']}"):
                    try:
                        dados = cache_xano.carregar_cache(
                            st.session_state,
                            credencial.token,
                            f"paciente:{paciente['id']}",
                            lambda: cliente.obter_paciente(credencial.token, paciente["id"]),
                        )
                        _limpar_edicao()
                        st.session_state[CHAVE_EDICAO] = {
                            "sessao": identificador_sessao, "paciente": dados,
                        }
                        edicao = st.session_state[CHAVE_EDICAO]
                    except ErroAcesso as error:
                        if error.status == 404 and not st.session_state.pop("pacientes_xano_edit_retry", False):
                            # A lista pode ter sido atualizada depois do cache;
                            # refaz uma leitura antes de confirmar o 404.
                            cache_xano.invalidar_cache(st.session_state, namespaces=["pacientes", "agenda/opcoes"])
                            st.session_state["pacientes_xano_edit_retry"] = True
                            st.rerun()
                        st.session_state.pop("pacientes_xano_edit_retry", None)
                        if error.status == 401:
                            sessao.limpar(st.session_state)
                            st.error("Sua sessão expirou. Entre novamente para editar o Paciente.")
                            return
                        if error.status == 403:
                            st.error("Sua Conta de Acesso não tem permissão para editar Pacientes.")
                            return
                        st.error(_mensagem_edicao(error))
                        return
                st.divider()

    edicao = st.session_state.get(CHAVE_EDICAO)
    if edicao:
        _renderizar_edicao(cliente, credencial, edicao)
