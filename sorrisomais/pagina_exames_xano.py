"""Tela de Exames seguindo a composição Sorriso Mais e autorização do Xano."""

from datetime import date

import streamlit as st

from . import sessao
from .api import ErroAcesso
from .exames_api import ClienteExames, SITUACOES_EXAME


def _cartao(exame, *, profissional=False, cliente=None, token=None):
    with st.container(border=True):
        st.subheader(exame.get("tipo") or "Exame")
        st.caption(f"Situação · {exame.get('situacao', 'Solicitado')}")
        if exame.get("solicitado_em"):
            st.caption(f"Solicitado em {exame['solicitado_em'][:10]}")
        if profissional and exame.get("resultado"):
            st.write(exame["resultado"])
        elif exame.get("situacao") == "Resultado disponível":
            st.write(exame.get("resultado") or "Resultado sem texto informado.")
        else:
            st.info("Resultado ainda não liberado para este Paciente.")


def renderizar(cliente, conta):
    st.caption("ATENDIMENTO CLÍNICO  /  EXAMES")
    st.title("Exames")
    st.markdown("Acompanhe solicitações e resultados com acesso controlado pelo Xano.")
    perfis = set(getattr(conta, "perfis", ()))
    if not perfis.intersection({"profissional", "paciente"}):
        st.warning("O acesso a Exames não está disponível para este perfil.")
        return
    credencial = st.session_state.get(sessao.CHAVE)
    if not credencial:
        st.error("Sua sessão não está disponível. Entre novamente.")
        return
    api = ClienteExames(cliente)
    try:
        exames = api.listar(credencial.token)
    except ErroAcesso as error:
        if error.status == 401:
            sessao.limpar(st.session_state)
            st.error("Sua sessão expirou. Entre novamente.")
        else:
            st.error("Não foi possível carregar os Exames. Tente novamente em instantes.")
        return
    except Exception:
        st.error("Não foi possível carregar os Exames. Tente novamente em instantes.")
        return
    if "profissional" in perfis:
        with st.expander("Solicitar exame", expanded=False):
            with st.form("form-solicitar-exame", border=True):
                paciente_id = st.number_input("Paciente *", min_value=1, step=1)
                consulta_id = st.number_input("Consulta *", min_value=1, step=1)
                tipo = st.text_input("Tipo do exame *", max_chars=160)
                solicitado_em = st.date_input("Data da solicitação", value=date.today())
                observacoes = st.text_area("Observações", max_chars=1000)
                if st.form_submit_button("Solicitar exame", type="primary"):
                    try:
                        api.solicitar(credencial.token, paciente_id=int(paciente_id), consulta_id=int(consulta_id), tipo=tipo, solicitado_em=solicitado_em.isoformat(), observacoes=observacoes)
                        st.success("Exame solicitado.")
                    except ErroAcesso as error:
                        st.error(str(error))
    if not exames:
        st.info("Nenhum Exame encontrado neste escopo.")
        return
    for exame in exames:
        _cartao(exame, profissional="profissional" in perfis)
