"""Visão geral diária do Profissional autenticado."""

from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

import streamlit as st

from . import navegacao, sessao
from .api import ErroAcesso

FUSO_CLINICA = ZoneInfo("America/Sao_Paulo")


def _intervalo_hoje():
    hoje = datetime.now(FUSO_CLINICA).date()
    inicio = datetime.combine(hoje, time.min, tzinfo=FUSO_CLINICA)
    fim = inicio + timedelta(days=1)
    return hoje, inicio.isoformat(timespec="seconds"), fim.isoformat(timespec="seconds")


def _horario(consulta):
    valor = datetime.fromisoformat(consulta["inicio_em"].replace("Z", "+00:00"))
    return valor.astimezone(FUSO_CLINICA)


def renderizar(cliente, conta):
    hoje, inicio, fim = _intervalo_hoje()
    credencial = st.session_state.get(sessao.CHAVE)
    dia_semana = ("SEGUNDA-FEIRA", "TERÇA-FEIRA", "QUARTA-FEIRA", "QUINTA-FEIRA",
                  "SEXTA-FEIRA", "SÁBADO", "DOMINGO")[hoje.weekday()]
    meses = ("JANEIRO", "FEVEREIRO", "MARÇO", "ABRIL", "MAIO", "JUNHO",
             "JULHO", "AGOSTO", "SETEMBRO", "OUTUBRO", "NOVEMBRO", "DEZEMBRO")
    st.caption(f"{dia_semana}, {hoje.day} DE {meses[hoje.month - 1]}")
    nome = conta.nome.split()[0] if conta.nome.strip() else "Profissional"
    st.title(f"Olá, {nome}! 👋")
    st.caption("Aqui está sua agenda de hoje.")

    try:
        consultas = cliente.listar_consultas(credencial.token, inicio=inicio, fim=fim)
    except ErroAcesso as error:
        if error.status in (401, 403):
            sessao.limpar(st.session_state)
            st.error("Sua sessão expirou. Entre novamente." if error.status == 401
                     else "Sua Conta de Acesso não tem permissão para consultar esta agenda.")
            return
        st.error("Não foi possível carregar sua agenda. Tente novamente.")
        if st.button("Tentar novamente", key="painel-profissional-retry"):
            st.rerun()
        consultas = None

    if consultas is None:
        return

    try:
        consultas.sort(key=lambda item: (_horario(item), item["id"]))
    except (KeyError, TypeError, ValueError):
        st.error("Não foi possível carregar sua agenda. Tente novamente.")
        if st.button("Tentar novamente", key="painel-profissional-retry-resposta"):
            st.rerun()
        return
    agora = datetime.now(FUSO_CLINICA)
    futuras = [item for item in consultas if _horario(item) >= agora
               and item["situacao"] not in {"Cancelada", "Falta", "Realizada"}]
    proxima = futuras[0] if futuras else None
    concluidas = sum(item["situacao"] == "Realizada" for item in consultas)
    metricas = st.columns(3, gap="small")
    for coluna, rotulo, valor, detalhe in (
        (metricas[0], "Consultas hoje", str(len(consultas)), "na sua agenda"),
        (metricas[1], "Atendimentos", str(concluidas), "realizados hoje"),
        (metricas[2], "Próxima consulta", _horario(proxima).strftime("%H:%M") if proxima else "—",
         proxima["paciente_nome"] if proxima else "nenhuma marcada"),
    ):
        with coluna, st.container(border=True):
            st.caption(rotulo)
            st.markdown(f"<strong class='valor-metrica'>{valor}</strong>", unsafe_allow_html=True)
            st.caption(detalhe)

    agenda, atalhos = st.columns([1.75, 1], gap="medium", vertical_alignment="top")
    with agenda, st.container(key="painel-profissional-agenda", border=True):
        cabecalho, abrir = st.columns([2, 1], vertical_alignment="center")
        cabecalho.subheader("Agenda de hoje")
        abrir.button("Ver agenda completa →", key="painel-profissional-abrir-agenda",
                     on_click=lambda: st.session_state.__setitem__("pagina_equipe", "agenda"),
                     width="stretch")
        st.caption(f"{len(consultas)} consulta(s) agendada(s)")
        st.divider()
        if not consultas:
            st.info("Nenhuma consulta para hoje.")
        for consulta in consultas:
            horario = _horario(consulta)
            with st.container(key=f"painel-profissional-consulta-{consulta['id']}"):
                hora, dados, situacao = st.columns([0.65, 2.8, 1], vertical_alignment="center")
                hora.markdown(f"**{horario:%H:%M}**")
                dados.markdown(f"**{consulta['paciente_nome']}**")
                detalhes = " · ".join(consulta["procedimentos"])
                dados.caption(detalhes or "Procedimento não informado")
                situacao.caption(consulta["situacao"])
            st.divider()

    with atalhos, st.container(key="painel-profissional-atalhos", border=True):
        st.subheader("Acesso rápido")
        if navegacao.modulo_xano_disponivel("prontuarios"):
            st.button("▤  Abrir prontuário", key="painel-profissional-prontuario",
                      on_click=lambda: st.session_state.__setitem__("pagina_equipe", "prontuarios"),
                      width="stretch")
        else:
            st.info("A listagem de Prontuários ainda não está integrada ao Xano.")
        st.button("□  Visualizar agenda", key="painel-profissional-agenda-atalho",
                  on_click=lambda: st.session_state.__setitem__("pagina_equipe", "agenda"),
                  width="stretch")
