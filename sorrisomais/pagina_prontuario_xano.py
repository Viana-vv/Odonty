"""Histórico individual do Prontuário integrado aos contratos existentes do Xano."""

import hashlib
import time
from datetime import datetime
from zoneinfo import ZoneInfo

import streamlit as st

from . import sessao
from .api import ErroAcesso
from . import pagina_nova_evolucao_xano

_CHAVE_CACHE_HISTORICO = "prontuario_historico_cache"
_CACHE_HISTORICO_SEGUNDOS = 20


def _carregar_dados(cliente, token):
    """Reutiliza respostas bem-sucedidas durante reruns da mesma sessão."""
    identificador_token = hashlib.sha256(token.encode("utf-8")).hexdigest()
    agora = time.monotonic()
    cache = st.session_state.get(_CHAVE_CACHE_HISTORICO)
    if (isinstance(cache, dict)
            and cache.get("token") == identificador_token
            and agora - cache.get("instante", 0) < _CACHE_HISTORICO_SEGUNDOS):
        return cache["consultas"], cache["registros"]

    st.session_state.pop(_CHAVE_CACHE_HISTORICO, None)
    consultas = cliente.listar_consultas(token)
    registros = cliente.listar_registros_clinicos(token)
    st.session_state[_CHAVE_CACHE_HISTORICO] = {
        "token": identificador_token,
        "instante": time.monotonic(),
        "consultas": consultas,
        "registros": registros,
    }
    return consultas, registros


def _pacientes_disponiveis(consultas, registros):
    pacientes = {}
    for consulta in consultas:
        paciente_id = consulta.get("paciente_id")
        if isinstance(paciente_id, int):
            nome = consulta.get("paciente_nome")
            pacientes[paciente_id] = nome if isinstance(nome, str) and nome.strip() else f"ID {paciente_id}"
    for registro in registros:
        paciente_id = registro.get("paciente_id")
        if isinstance(paciente_id, int) and paciente_id not in pacientes:
            pacientes[paciente_id] = f"ID {paciente_id}"
    return pacientes


def _data_legivel(valor):
    if not isinstance(valor, str):
        return "Data não informada"
    try:
        data = datetime.fromisoformat(valor.replace("Z", "+00:00"))
    except ValueError:
        return "Data não informada"
    fuso_local = ZoneInfo("America/Sao_Paulo")
    if data.tzinfo is None:
        data = data.replace(tzinfo=fuso_local)
    return data.astimezone(fuso_local).strftime("%d/%m/%Y às %H:%M")


def _renderizar_historico(registros):
    if not registros:
        st.info("Este Paciente ainda não possui Registros Clínicos disponíveis.")
        return
    for registro in registros:
        with st.container(key=f"cartao-registro-clinico-{registro.get('id', 'sem-id')}", border=True):
            paciente = registro.get("paciente_nome")
            profissional = registro.get("profissional_nome")
            data = registro.get("registrado_em")
            col_identidade, col_profissional = st.columns([1, 1], vertical_alignment="center")
            with col_identidade:
                if isinstance(paciente, str) and paciente.strip():
                    st.subheader(paciente)
                else:
                    st.subheader("Registro Clínico")
                st.caption(_data_legivel(data))
            if isinstance(profissional, str) and profissional.strip():
                with col_profissional:
                    st.caption(f"Profissional responsável · {profissional}")
            conteudo = registro.get("conteudo")
            if isinstance(conteudo, str) and conteudo.strip():
                with st.container(key=f"conteudo-registro-clinico-{registro.get('id', 'sem-id')}"):
                    st.write(conteudo)
            st.caption(f"Registro #{registro.get('id', '—')}")


def renderizar(cliente, conta):
    """Renderiza histórico somente para perfis clínicos reconhecidos."""
    titulo, acao = st.columns([1, 0.34], vertical_alignment="center")
    with titulo:
        st.caption("HISTÓRICO CLÍNICO")
        st.title("Prontuários")
        st.markdown("Registre evoluções e consulte os atendimentos realizados.")

    aviso = st.session_state.pop("prontuario_aviso", None)
    if aviso:
        st.success(aviso)

    perfis = set(getattr(conta, "perfis", ()))
    if not perfis.intersection({"profissional", "paciente"}):
        st.warning("O acesso a informações clínicas não está disponível para este perfil.")
        return

    credencial = st.session_state.get(sessao.CHAVE)
    if not credencial:
        st.error("Sua sessão não está disponível. Entre novamente.")
        return

    try:
        with st.spinner("Carregando histórico clínico…"):
            consultas, registros = _carregar_dados(cliente, credencial.token)
    except ErroAcesso as error:
        if error.status == 401:
            sessao.limpar(st.session_state)
            st.error("Sua sessão expirou. Entre novamente.")
        else:
            st.error(str(error))
        return
    except Exception:
        st.error("Não foi possível carregar o histórico clínico. Tente novamente em instantes.")
        return

    pacientes = _pacientes_disponiveis(consultas, registros)
    if not pacientes:
        st.info("Não há Pacientes ou Registros Clínicos disponíveis neste escopo.")
        return

    ids = list(pacientes)
    opcoes = [None, *ids]
    if st.session_state.get("prontuario_paciente_id") not in opcoes:
        st.session_state["prontuario_paciente_id"] = None
    nomes = {paciente_id: pacientes[paciente_id] for paciente_id in ids}

    with acao:
        if "profissional" in perfis:
            pagina_nova_evolucao_xano.renderizar(cliente, conta, consultas)

    seletor, aviso = st.columns([1, 1], vertical_alignment="bottom")
    with seletor:
        selecionado = st.selectbox(
            "Paciente", opcoes,
            format_func=lambda paciente_id: "Todos" if paciente_id is None else nomes[paciente_id],
            key="prontuario_paciente_id",
        )
    with aviso:
        st.caption("◉ Acesso clínico restrito")

    recentes, linha_tempo = st.columns([0.85, 1.8], gap="medium")
    with recentes:
        with st.container(key="lista-pacientes-recentes", border=True):
            st.subheader("Pacientes recentes")
            for paciente_id in ids:
                quantidade = sum(reg.get("paciente_id") == paciente_id for reg in registros)
                if st.button(
                    f"{nomes[paciente_id]}  ·  {quantidade} registro(s)  ›",
                    key=f"prontuario-paciente-{paciente_id}",
                    type="primary" if paciente_id == selecionado else "secondary",
                    width="stretch",
                ):
                    st.session_state["prontuario_paciente_id"] = paciente_id
                    st.rerun()
    with linha_tempo:
        registros_paciente = [
            registro for registro in registros
            if selecionado is None or registro.get("paciente_id") == selecionado
        ]
        _renderizar_historico(registros_paciente)
