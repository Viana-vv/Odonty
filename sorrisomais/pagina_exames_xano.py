"""Tela de Exames seguindo a composição Sorriso Mais e autorização do Xano."""

from datetime import date, datetime, time, timezone

import streamlit as st

from . import sessao
from .api import ErroAcesso
from .exames_api import ClienteExames


_FEEDBACK_CHAVE = "exames_feedback"


def _cartao(exame, *, profissional, api, token):
    identificador = exame.get("id")
    situacao = exame.get("situacao", "Solicitado")
    with st.container(border=True):
        st.subheader(exame.get("tipo") or "Exame")
        st.caption(f"Situação · {situacao}")
        if exame.get("solicitado_em"):
            st.caption(f"Solicitado em {exame['solicitado_em'][:10]}")

        if profissional:
            if exame.get("resultado"):
                st.write(exame["resultado"])
            transicoes = {
                "Solicitado": ("Realizado", "Cancelado", "Não realizado"),
                "Realizado": ("Resultado disponível",),
            }
            opcoes = transicoes.get(situacao, ())
            if opcoes:
                with st.expander("Atualizar situação", expanded=False):
                    with st.form(f"form-atualizar-exame-{identificador}", border=True):
                        nova_situacao = st.selectbox(
                            "Nova situação", opcoes, key=f"exame-situacao-{identificador}"
                        )
                        realizado_em = None
                        resultado = None
                        if nova_situacao in ("Realizado", "Resultado disponível"):
                            data_realizacao = st.date_input(
                                "Data da realização *",
                                value=date.today(),
                                key=f"exame-data-realizacao-{identificador}",
                            )
                            realizado_em = datetime.combine(
                                data_realizacao, time.min, tzinfo=timezone.utc
                            ).isoformat()
                        if nova_situacao == "Resultado disponível":
                            resultado = st.text_area(
                                "Resultado *", max_chars=4000,
                                key=f"exame-resultado-{identificador}",
                            )
                        observacoes = st.text_area(
                            "Observações", max_chars=1000,
                            key=f"exame-observacoes-{identificador}",
                        )
                        if st.form_submit_button("Salvar atualização", type="primary"):
                            if nova_situacao == "Resultado disponível" and not (resultado or "").strip():
                                st.error("Informe o resultado antes de disponibilizá-lo ao Paciente.")
                                return
                            try:
                                api.atualizar_situacao(
                                    token,
                                    identificador,
                                    situacao=nova_situacao,
                                    resultado=resultado,
                                    realizado_em=realizado_em,
                                    observacoes=observacoes,
                                )
                                st.session_state[_FEEDBACK_CHAVE] = "Situação do Exame atualizada."
                                st.rerun()
                            except ErroAcesso as error:
                                if error.status == 401:
                                    sessao.limpar(st.session_state)
                                    st.error("Sua sessão expirou. Entre novamente.")
                                else:
                                    st.error("Não foi possível atualizar o Exame. Confira os dados e tente novamente.")
        elif situacao == "Resultado disponível":
            st.write(exame.get("resultado") or "Resultado sem texto informado.")
        else:
            st.info("Resultado ainda não liberado para este Paciente.")


def renderizar(cliente, conta):
    st.title("Exames")
    st.markdown("Acompanhe solicitações e resultados dos Exames.")
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
        with st.spinner("Carregando Exames…"):
            exames = api.listar(credencial.token)
    except ErroAcesso as error:
        if error.status == 401:
            sessao.limpar(st.session_state)
            st.error("Sua sessão expirou. Entre novamente.")
        elif error.status == 403:
            st.error("Seu perfil não possui autorização para consultar Exames.")
        else:
            st.error("Não foi possível carregar os Exames. Tente novamente em instantes.")
            if st.button("Tentar novamente", key="exames-tentar-novamente"):
                st.rerun()
        return
    except Exception:
        st.error("Não foi possível carregar os Exames. Tente novamente em instantes.")
        if st.button("Tentar novamente", key="exames-tentar-novamente"):
            st.rerun()
        return

    feedback = st.session_state.pop(_FEEDBACK_CHAVE, None)
    if feedback:
        st.success(feedback)
    if st.button("Atualizar exames", key="exames-atualizar-lista"):
        st.rerun()

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
                        api.solicitar(
                            credencial.token,
                            paciente_id=int(paciente_id),
                            consulta_id=int(consulta_id),
                            tipo=tipo,
                            solicitado_em=solicitado_em.isoformat(),
                            observacoes=observacoes,
                        )
                        st.session_state[_FEEDBACK_CHAVE] = "Exame solicitado."
                        st.rerun()
                    except ErroAcesso as error:
                        if error.status == 401:
                            sessao.limpar(st.session_state)
                            st.error("Sua sessão expirou. Entre novamente.")
                        else:
                            st.error("Não foi possível solicitar o Exame. Confira os dados e tente novamente.")

    if not exames:
        st.info("Nenhum Exame encontrado neste escopo.")
        return
    for exame in exames:
        _cartao(
            exame,
            profissional="profissional" in perfis,
            api=api,
            token=credencial.token,
        )
