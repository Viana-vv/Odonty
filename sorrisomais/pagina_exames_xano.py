"""Tela de Exames seguindo a composição Sorriso Mais e autorização do Xano."""

from datetime import date, datetime
from zoneinfo import ZoneInfo

import streamlit as st

from . import sessao
from .api import ErroAcesso
from .exames_api import ClienteExames, SITUACOES_EXAME

_FUSO_CLINICA = ZoneInfo("America/Sao_Paulo")


def _rotulo_consulta(consulta, pacientes):
    try:
        inicio = datetime.fromisoformat(consulta["inicio_em"].replace("Z", "+00:00"))
        if inicio.tzinfo is None:
            inicio = inicio.replace(tzinfo=_FUSO_CLINICA)
        inicio = inicio.astimezone(_FUSO_CLINICA)
    except (KeyError, TypeError, ValueError):
        return f"Consulta {consulta['id']} · data indisponível"
    paciente = pacientes.get(consulta.get("paciente_id"), "Paciente")
    return f"{inicio:%d/%m/%Y às %H:%M} · {paciente} · {consulta.get('situacao', 'Consulta')}"


def _opcoes_solicitacao(cliente, token):
    """Carrega dados administrativos e Consultas autorizadas, com cache por sessão."""
    from .pagina_nova_consulta_xano import _leitura_com_cache

    opcoes = _leitura_com_cache(
        token, ("exames-solicitacao-opcoes",),
        lambda: cliente.listar_opcoes_agenda(token),
    )
    consultas = _leitura_com_cache(
        token, ("exames-solicitacao-consultas",),
        lambda: cliente.listar_consultas(token),
    )
    return opcoes, consultas


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
            try:
                opcoes, consultas_disponiveis = _opcoes_solicitacao(
                    cliente, credencial.token
                )
            except ErroAcesso as error:
                if error.status == 401:
                    sessao.limpar(st.session_state)
                    st.error("Sua sessão expirou. Entre novamente.")
                else:
                    st.error("Não foi possível carregar Pacientes e Consultas. Tente novamente.")
                return
            except Exception:
                st.error("Não foi possível carregar Pacientes e Consultas. Tente novamente.")
                return

            pacientes_lista = opcoes.get("pacientes", []) if isinstance(opcoes, dict) else []
            pacientes = {
                item["id"]: item["nome"].strip()
                for item in pacientes_lista
                if isinstance(item, dict) and type(item.get("id")) is int
                and isinstance(item.get("nome"), str) and item["nome"].strip()
            }
            if not pacientes:
                st.info("Cadastre Pacientes ativos antes de solicitar um Exame.")
                return
            paciente_id = st.selectbox(
                "Paciente *", list(pacientes), format_func=pacientes.get,
                key="exame-paciente",
            )
            consultas = {
                item["id"]: item for item in consultas_disponiveis
                if isinstance(item, dict) and type(item.get("id")) is int
                and item.get("paciente_id") == paciente_id
                and item["id"] > 0
            } if isinstance(consultas_disponiveis, list) else {}
            if not consultas:
                st.info("Este Paciente ainda não possui Consultas disponíveis para vincular ao Exame.")
                return
            with st.form("form-solicitar-exame", border=True):
                consulta_id = st.selectbox(
                    "Consulta *", list(consultas),
                    format_func=lambda identificador: _rotulo_consulta(
                        consultas[identificador], pacientes
                    ),
                    key="exame-consulta",
                )
                tipo = st.text_input("Tipo do exame *", max_chars=160)
                solicitado_em = st.date_input("Data da solicitação", value=date.today())
                observacoes = st.text_area("Observações", max_chars=1000)
                if st.form_submit_button("Solicitar exame", type="primary"):
                    try:
                        api.solicitar(
                            credencial.token, paciente_id=paciente_id,
                            consulta_id=consulta_id, tipo=tipo,
                            solicitado_em=solicitado_em.isoformat(),
                            observacoes=observacoes,
                        )
                        st.success("Exame solicitado.")
                    except ErroAcesso as error:
                        st.error(str(error))
    if not exames:
        st.info("Nenhum Exame encontrado neste escopo.")
        return
    for exame in exames:
        _cartao(exame, profissional="profissional" in perfis)
