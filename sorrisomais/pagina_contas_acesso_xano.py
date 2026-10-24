"""Consulta administrativa e somente leitura de Contas de Acesso."""

import streamlit as st

from . import api_contas_acesso, sessao
from .api import ErroAcesso

_ROTULOS_PERFIS = {
    "paciente": "Paciente",
    "profissional": "Profissional",
    "administrador": "Administrador",
    "recepcionista": "Recepcionista",
}


def _iniciais(nome):
    return "".join(parte[0] for parte in nome.split()[:2]).upper() or "C"


def renderizar(cliente, conta):
    st.caption("EQUIPE DA CLÍNICA")
    perfis = set(getattr(conta, "perfis", ()))
    titulo, acao_atualizar = st.columns([5, 1], vertical_alignment="center")
    titulo.title("Contas de Acesso")
    titulo.write("Consulte as contas cadastradas e seus perfis de acesso.")

    if not perfis.intersection({"administrador", "recepcionista"}):
        st.info("Seu perfil não tem permissão para consultar esta lista.")
        return

    credencial = st.session_state.get(sessao.CHAVE)
    if credencial is None:
        st.error("Sua sessão expirou. Entre novamente para consultar as Contas de Acesso.")
        return

    atualizar = acao_atualizar.button(
        "Atualizar lista", key="contas-acesso-atualizar", width="stretch",
    )

    try:
        mensagem_carregamento = (
            "Atualizando Contas de Acesso…" if atualizar
            else "Carregando Contas de Acesso…"
        )
        with st.spinner(mensagem_carregamento):
            contas = api_contas_acesso.listar_contas_acesso(cliente, credencial.token)
    except ErroAcesso as error:
        if error.status == 401:
            sessao.limpar(st.session_state)
            st.rerun()
            return
        elif error.status == 403:
            st.error("Sua Conta de Acesso não tem permissão para consultar esta lista.")
        else:
            st.error("Não foi possível carregar as Contas de Acesso. Tente novamente em instantes.")
        return

    if not contas:
        st.info("Não há Contas de Acesso cadastradas para exibir.")
        return

    st.caption(f"{len(contas)} conta(s)")
    for inicio in range(0, len(contas), 3):
        colunas = st.columns(3, gap="medium")
        for coluna, item in zip(colunas, contas[inicio:inicio + 3]):
            with coluna:
                with st.container(border=True, key=f"conta-acesso-{item['id']}"):
                    avatar, resumo = st.columns([1, 3], vertical_alignment="center")
                    avatar.markdown(f"### {_iniciais(item['nome'])}")
                    resumo.caption(item["situacao"].capitalize())
                    st.subheader(item["nome"])
                    st.caption(f"ID {item['id']}")
                    st.write(f"E-mail: {item['email']}")
                    st.write("Perfis: " + ", ".join(
                        _ROTULOS_PERFIS[perfil] for perfil in item["perfis"]
                    ))
