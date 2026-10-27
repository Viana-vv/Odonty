"""Consulta e gestão administrativa de Profissionais conectados ao Xano."""

import time

import streamlit as st

from .api import ErroAcesso
from . import sessao
from .cache_xano import carregar_cache, invalidar_cache



def _iniciais(nome):
    partes = nome.split()
    return "".join(parte[0] for parte in partes[:2]).upper() or "P"


def _listar_profissionais(cliente, token, estado, atualizar=False):
    return carregar_cache(estado, token, "profissionais", lambda: cliente.listar_profissionais(token), force=atualizar)


def _situacao_card(cliente, profissional, token, estado, administrador):
    ativo = profissional["situacao"] == "ativo"
    st.caption("Ativo" if ativo else "Inativo")
    if not administrador:
        # O chamador usa ``None`` para sinalizar falha de autenticação durante
        # uma alteração de situação. Para um cartão somente de leitura, use o
        # mesmo sentinela de operação concluída utilizado pelo administrador;
        # caso contrário a primeira ficha encerra a renderização da lista.
        return False

    proxima = "inativo" if ativo else "ativo"
    acao = "Inativar" if ativo else "Ativar"
    confirmar = st.checkbox(
        f"Confirmo {acao.lower()} {profissional['nome']}",
        key=f"profissional-confirmar-{profissional['id']}",
    )
    if st.button(
        f"Confirmar {acao.lower()}", key=f"profissional-situacao-{profissional['id']}",
        disabled=not confirmar,
    ):
        invalidar_cache(estado)
        try:
            cliente.atualizar_situacao_profissional(token, profissional["id"], proxima)
            profissionais = _listar_profissionais(cliente, token, estado, atualizar=True)
            st.success(f"Situação de {profissional['nome']} atualizada.")
            st.rerun()
            return profissionais
        except ErroAcesso as error:
            if error.status == 401:
                sessao.limpar(estado)
            st.error(str(error))
            return None
    return False


def renderizar(cliente, conta):
    """Exibe Profissionais e permite alterar situação apenas ao Administrador."""
    st.caption("EQUIPE DA CLÍNICA")
    st.title("Profissionais")
    st.write("Consulte os dados cadastrais dos Profissionais da clínica.")

    perfis = set(conta.perfis)
    if not perfis.intersection({"administrador", "recepcionista"}):
        st.info("Seu perfil não tem permissão para consultar esta lista.")
        return

    credencial = st.session_state.get(sessao.CHAVE)
    if credencial is None:
        st.error("Sua sessão expirou. Entre novamente para consultar os Profissionais.")
        return

    atualizar = st.button("Atualizar lista", key="profissionais-xano-atualizar")
    try:
        with st.spinner("Carregando Profissionais..."):
            profissionais = _listar_profissionais(
                cliente, credencial.token, st.session_state, atualizar=atualizar,
            )
    except ErroAcesso as error:
        if error.status == 401:
                sessao.limpar(st.session_state)
        st.error(str(error))
        return

    administrador = "administrador" in perfis
    profissionais_visiveis = (profissionais if administrador else
                               [item for item in profissionais if item.get("situacao") == "ativo"])
    profissionais = profissionais_visiveis
    if not profissionais:
        st.info("Não há Profissionais cadastrados para exibir.")
        return

    st.caption(f"{len(profissionais)} profissional(is)")
    colunas = st.columns(3, gap="medium")
    for indice, profissional in enumerate(profissionais):
        coluna = colunas[indice % len(colunas)]
        with coluna:
            with st.container(border=True, key=f"profissional-xano-{profissional['id']}"):
                avatar, resumo = st.columns([1, 2], vertical_alignment="center")
                avatar.markdown(f"### {_iniciais(profissional['nome'])}")
                resumo.caption(profissional["cro"])
                st.subheader(profissional["nome"])
                st.write(f"Especialidade: {profissional['especialidade']['nome']}")
                st.write(f"E-mail: {profissional['email'] or 'Não informado'}")
                st.write(f"Telefone: {profissional['telefone'] or 'Não informado'}")
                resultado = _situacao_card(
                    cliente, profissional, credencial.token, st.session_state,
                    administrador=administrador,
                )
                if resultado is None:
                    return
                if isinstance(resultado, list):
                    profissionais = resultado
                    # Uma mutação por execução; a lista é confirmada novamente pelo Xano.
                    return
