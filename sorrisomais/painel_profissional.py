"""Visão geral diária do Profissional autenticado."""

from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

import streamlit as st

from . import navegacao, sessao, ilustracoes
from .api import ErroAcesso

FUSO_CLINICA = ZoneInfo("America/Sao_Paulo")
SITUACOES_TERMINAIS = {"Cancelada", "Falta", "Realizada"}


def _intervalo_hoje():
    hoje = datetime.now(FUSO_CLINICA).date()
    inicio = datetime.combine(hoje, time.min, tzinfo=FUSO_CLINICA)
    fim = inicio + timedelta(days=1)
    return hoje, inicio.isoformat(timespec="seconds"), fim.isoformat(timespec="seconds")


def _horario(consulta):
    valor = datetime.fromisoformat(consulta["inicio_em"].replace("Z", "+00:00"))
    if valor.tzinfo is None:
        raise ValueError("Horário sem fuso")
    return valor.astimezone(FUSO_CLINICA)


def _resumir_consultas(consultas):
    if not isinstance(consultas, list):
        raise ValueError("Resposta de Consultas inválida")

    resumo = []
    for consulta in consultas:
        if not isinstance(consulta, dict):
            raise ValueError("Consulta inválida")
        nome = consulta.get("paciente_nome")
        situacao = consulta.get("situacao")
        if not isinstance(nome, str) or not nome.strip() or not isinstance(situacao, str):
            raise ValueError("Campos da Consulta inválidos")
        situacao = "Realizada" if situacao == "Concluída" else situacao
        resumo.append({
            "horario": _horario(consulta),
            "paciente_nome": nome.strip(),
            "situacao": situacao,
        })
    return sorted(resumo, key=lambda consulta: consulta["horario"])


def _iniciais(nome):
    partes = nome.split()
    letras = "".join(parte[0] for parte in partes[:2] if parte and parte[0].isalnum())
    return letras.upper() or "?"


def _erro_carregamento(error):
    if error.status == 401:
        sessao.limpar(st.session_state)
        st.error("Sua sessão expirou. Entre novamente.")
        return
    if error.status == 403:
        st.error("Sua Conta de Acesso não tem permissão para consultar esta agenda.")
        return
    st.error("Não foi possível carregar sua agenda. Tente novamente.")
    if st.button("Tentar novamente", key="painel-profissional-retry"):
        st.rerun()


def _renderizar_metricas(consultas, agora):
    futuras = [consulta for consulta in consultas
               if consulta["horario"] >= agora
               and consulta["situacao"] not in SITUACOES_TERMINAIS]
    proxima = futuras[0] if futuras else None
    realizadas = sum(consulta["situacao"] == "Realizada" for consulta in consultas)
    confirmadas = sum(consulta["situacao"] == "Confirmada" for consulta in consultas)
    valores = (
        ("Consultas hoje", str(len(consultas)), "na sua agenda", "▦"),
        ("Atendimentos", str(realizadas), "realizados hoje", "✓"),
        ("Confirmadas", str(confirmadas), "para hoje", "▤"),
        ("Próxima consulta", proxima["horario"].strftime("%H:%M") if proxima else "—",
         proxima["paciente_nome"] if proxima else "nenhuma marcada", "◷"),
    )
    with st.container(key="painel-profissional-metricas"):
        metricas = st.columns(4, gap="small")
        for indice, (coluna, (rotulo, valor, detalhe, icone)) in enumerate(zip(metricas, valores)):
            with coluna, st.container(key=f"painel-profissional-metrica-{indice}", border=True):
                st.markdown(f"<span class='icone-metrica'>{icone}</span>", unsafe_allow_html=True)
                st.caption(rotulo)
                st.markdown(f"<strong class='valor-metrica'>{valor}</strong>", unsafe_allow_html=True)
                st.caption(detalhe)


def _renderizar_agenda(consultas):
    with st.container(key="painel-profissional-agenda", border=True):
        cabecalho, abrir = st.columns([2, 1], vertical_alignment="center")
        cabecalho.subheader("Agenda de hoje")
        abrir.button(
            "Ver agenda completa →", key="painel-profissional-abrir-agenda",
            on_click=lambda: st.session_state.__setitem__("pagina_equipe", "agenda"),
            width="stretch",
        )
        st.caption(f"{len(consultas)} consulta(s) agendada(s)")
        st.divider()
        if not consultas:
            with st.container(key="painel-profissional-estado-vazio"):
                st.info("Nenhuma consulta para hoje.")
            return

        for indice, consulta in enumerate(consultas[:5]):
            with st.container(key=f"painel-profissional-consulta-{indice}"):
                hora, avatar, dados, situacao = st.columns([0.65, 0.55, 2.8, 1], vertical_alignment="center")
                hora.markdown(f"**{consulta['horario']:%H:%M}**")
                avatar.markdown(f"<span class='painel-profissional-avatar'>{_iniciais(consulta['paciente_nome'])}</span>",
                                unsafe_allow_html=True)
                dados.text(consulta["paciente_nome"])
                situacao.caption(consulta["situacao"])
            if indice < min(len(consultas), 5) - 1:
                st.divider()


def _renderizar_atalhos():
    with st.container(key="painel-profissional-atalhos", border=True):
        st.subheader("Acesso rápido")
        if navegacao.modulo_xano_disponivel("prontuarios"):
            st.button(
                "▤  Abrir prontuário", key="painel-profissional-prontuario",
                on_click=lambda: st.session_state.__setitem__("pagina_equipe", "prontuarios"),
                width="stretch",
            )
        else:
            st.info("A listagem de Prontuários ainda não está integrada ao Xano.")
        st.button(
            "▦  Visualizar agenda", key="painel-profissional-agenda-atalho",
            on_click=lambda: st.session_state.__setitem__("pagina_equipe", "agenda"),
            width="stretch",
        )


def renderizar(cliente, conta):
    hoje, inicio, _fim = _intervalo_hoje()
    credencial = st.session_state.get(sessao.CHAVE)
    dias_semana = ("SEGUNDA-FEIRA", "TERÇA-FEIRA", "QUARTA-FEIRA", "QUINTA-FEIRA",
                   "SEXTA-FEIRA", "SÁBADO", "DOMINGO")
    meses = ("JANEIRO", "FEVEREIRO", "MARÇO", "ABRIL", "MAIO", "JUNHO",
             "JULHO", "AGOSTO", "SETEMBRO", "OUTUBRO", "NOVEMBRO", "DEZEMBRO")
    st.caption(f"{dias_semana[hoje.weekday()]}, {hoje.day} DE {meses[hoje.month - 1]}")
    nome = conta.nome.split()[0] if conta.nome.strip() else "Profissional"
    st.title(f"Olá, {nome}! 👋")
    st.caption("Aqui está sua agenda de hoje.")
    ilustracoes.banner_contextual("16-acompanhamento.png", "", "Seus atendimentos", "Acompanhe sua agenda, consulte Prontuários e registre evoluções.")

    try:
        if credencial is None:
            raise ErroAcesso("Sessão ausente", 401)
        # A Agenda já centraliza o cache curto, a identidade da Conta de Acesso,
        # a data consultada e o intervalo local enviado ao Xano.
        from . import paginas_equipe
        consultas_brutas = paginas_equipe._carregar_consultas_agenda(
            cliente, credencial.token, hoje
        )
        consultas = _resumir_consultas(consultas_brutas)
    except ErroAcesso as error:
        _erro_carregamento(error)
        return
    except (KeyError, TypeError, ValueError, AttributeError):
        st.error("Não foi possível carregar sua agenda. Tente novamente.")
        if st.button("Tentar novamente", key="painel-profissional-retry-resposta"):
            st.rerun()
        return

    agora = datetime.now(FUSO_CLINICA)
    _renderizar_metricas(consultas, agora)

    with st.container(key="painel-profissional-conteudo"):
        agenda, atalhos = st.columns([1.75, 1], gap="medium", vertical_alignment="top")
        with agenda:
            _renderizar_agenda(consultas)
        with atalhos:
            _renderizar_atalhos()
