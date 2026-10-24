"""Páginas da equipe. A identidade é revalidada por app.py antes de renderizar."""
import hashlib
from datetime import date, datetime, time, timedelta
from pathlib import Path
from time import monotonic
from zoneinfo import ZoneInfo

import streamlit as st

from .api import ErroAcesso, ROTULOS
from . import sessao, pagina_paciente, navegacao

ESPECIALIDADES_CACHE_TTL_SEGUNDOS = 300
ESPECIALIDADES_RETRY_SEGUNDOS = 20
CACHE_PAINEL_RECEPCAO = "painel_recepcao_xano_cache"
PAINEL_RECEPCAO_CACHE_TTL_SEGUNDOS = 20
PAINEL_RECEPCAO_RETRY_SEGUNDOS = 20
PAINEL_ADMIN_CACHE_TTL_SEGUNDOS = 20
PAINEL_ADMIN_RETRY_SEGUNDOS = 20
CACHE_PAINEL_ADMIN = "painel_administrativo_xano_cache"
RAIZ = Path(__file__).resolve().parents[1]


def renderizar_marca_menu():
    with st.container(key="marca-menu"):
        imagem, nome = st.columns([0.42, 1], gap="small", vertical_alignment="center")
        imagem.image(str(RAIZ / "assets" / "mascote-sorriso.png"), width=56)
        nome.markdown("<div class='marca-menu-nome'>Sorriso<em>+</em></div>",
                      unsafe_allow_html=True)


def listar_especialidades_sessao(cliente, token):
    agora = monotonic()
    carregadas = st.session_state.get("cad_especialidades_cache")
    carregadas_em = st.session_state.get("cad_especialidades_cache_em", 0)
    if isinstance(carregadas, list) and agora - carregadas_em < ESPECIALIDADES_CACHE_TTL_SEGUNDOS:
        return carregadas
    erro_em = st.session_state.get("cad_especialidades_erro_em", 0)
    if agora - erro_em < ESPECIALIDADES_RETRY_SEGUNDOS:
        raise ErroAcesso("Aguarde alguns segundos antes de tentar carregar as especialidades novamente.", 429)
    try:
        carregadas = cliente.listar_especialidades(token)
    except ErroAcesso:
        st.session_state["cad_especialidades_erro_em"] = agora
        raise
    st.session_state["cad_especialidades_cache"] = carregadas
    st.session_state["cad_especialidades_cache_em"] = agora
    st.session_state.pop("cad_especialidades_erro_em", None)
    return carregadas


def limpar_formulario():
    cache_sessao = {"cad_especialidades_cache", "cad_especialidades_cache_em",
                    "cad_especialidades_erro_em"}
    for chave in list(st.session_state):
        if chave.startswith("cad_") and chave not in cache_sessao:
            del st.session_state[chave]


def _carregar_consultas_painel(cliente, credencial, dia, *, atualizar=False):
    """Cacheia somente o resumo administrativo desta sessão e deste dia."""
    if credencial.expira_em <= datetime.now(ZoneInfo("UTC")):
        st.session_state.pop(CACHE_PAINEL_RECEPCAO, None)
        raise ErroAcesso("Sua sessão expirou. Entre novamente para consultar o painel.", 401)
    identidade = hashlib.sha256(credencial.token.encode("utf-8")).hexdigest()
    erro_em = st.session_state.get("painel_recepcao_xano_erro_em", 0)
    decorrido = monotonic() - erro_em if erro_em else PAINEL_RECEPCAO_RETRY_SEGUNDOS
    if 0 <= decorrido < PAINEL_RECEPCAO_RETRY_SEGUNDOS:
        raise ErroAcesso("Muitas tentativas. Aguarde alguns segundos antes de tentar novamente.", 429)
    cache = st.session_state.get(CACHE_PAINEL_RECEPCAO)
    idade = monotonic() - cache.get("carregado_em", 0) if isinstance(cache, dict) else PAINEL_RECEPCAO_CACHE_TTL_SEGUNDOS
    if (not atualizar and isinstance(cache, dict)
            and cache.get("sessao") == identidade
            and cache.get("dia") == dia
            and 0 <= idade < PAINEL_RECEPCAO_CACHE_TTL_SEGUNDOS
            and isinstance(cache.get("consultas"), list)):
        return cache["consultas"], cache["carregado_em"]

    st.session_state.pop(CACHE_PAINEL_RECEPCAO, None)
    token = credencial.token
    resposta = cliente.listar_consultas(
        token, inicio=_data_api(dia), fim=_data_api(dia, True)
    )
    campos_resumo = ("id", "situacao", "inicio_em", "fim_em", "paciente_nome", "profissional_nome")
    consultas = []
    for consulta in resposta:
        resumo = {campo: consulta[campo] for campo in campos_resumo}
        # A tabela Xano mantém o valor legado "Concluída" para a situação do domínio "Realizada".
        if resumo["situacao"] == "Concluída":
            resumo["situacao"] = "Realizada"
        consultas.append(resumo)
    carregado_em = monotonic()
    st.session_state.pop("painel_recepcao_xano_erro_em", None)
    st.session_state[CACHE_PAINEL_RECEPCAO] = {
        "sessao": identidade,
        "dia": dia,
        "consultas": consultas,
        "carregado_em": carregado_em,
    }
    return consultas, carregado_em


def _horario_consulta(consulta):
    return datetime.fromisoformat(consulta["inicio_em"].replace("Z", "+00:00")).astimezone(
        ZoneInfo("America/Sao_Paulo")
    )


def _renderizar_painel_recepcao(cliente, conta, pode_cadastrar_paciente, pode_agendar):
    """Resumo administrativo da Recepção baseado apenas nas Consultas autorizadas pelo Xano."""
    agora = datetime.now(ZoneInfo("America/Sao_Paulo"))
    dia = agora.date()
    dias = ("SEGUNDA-FEIRA", "TERÇA-FEIRA", "QUARTA-FEIRA", "QUINTA-FEIRA",
            "SEXTA-FEIRA", "SÁBADO", "DOMINGO")
    meses = ("JANEIRO", "FEVEREIRO", "MARÇO", "ABRIL", "MAIO", "JUNHO",
             "JULHO", "AGOSTO", "SETEMBRO", "OUTUBRO", "NOVEMBRO", "DEZEMBRO")
    st.caption(f"{dias[dia.weekday()]}, {dia.day} DE {meses[dia.month - 1]}")
    titulo, acao = st.columns([3, 1], vertical_alignment="center")
    primeiro_nome = conta.nome.split()[0] if conta.nome.strip() else "equipe"
    titulo.title(f"Olá, {primeiro_nome}! 👋")
    titulo.caption("Aqui está um resumo da clínica hoje.")
    consulta_integrada = navegacao.modulo_xano_disponivel("nova_consulta")
    if pode_agendar:
        acao.button(
            "+ Nova consulta", key="inicio-nova-consulta",
            on_click=abrir_nova_consulta if consulta_integrada else None,
            disabled=not consulta_integrada, width="stretch",
            help=None if consulta_integrada else "A tela Nova Consulta ainda não está integrada ao Xano.",
        )

    credencial = st.session_state.get(sessao.CHAVE)
    consultas = None
    carregado_em = None
    erro_carregamento = None
    atualizar = st.button("Atualizar resumo", key="inicio-painel-atualizar")
    if not credencial:
        st.session_state.pop(CACHE_PAINEL_RECEPCAO, None)
        st.session_state.pop("painel_recepcao_xano_erro_em", None)
        erro_carregamento = "Sua sessão expirou. Entre novamente para consultar o painel."
    else:
        try:
            with st.spinner("Carregando o resumo do dia…"):
                consultas, carregado_em = _carregar_consultas_painel(
                    cliente, credencial, dia, atualizar=atualizar
                )
        except ErroAcesso as error:
            st.session_state.pop(CACHE_PAINEL_RECEPCAO, None)
            if error.status == 401:
                st.session_state.pop("painel_recepcao_xano_erro_em", None)
                sessao.limpar(st.session_state)
                erro_carregamento = "Sua sessão expirou. Entre novamente para consultar o painel."
            elif error.status == 403:
                st.session_state.pop("painel_recepcao_xano_erro_em", None)
                erro_carregamento = "Sua Conta de Acesso não tem permissão para consultar este painel."
            elif error.status == 429:
                tentativa_erro_em = st.session_state.get("painel_recepcao_xano_erro_em", 0)
                if (not tentativa_erro_em
                        or monotonic() - tentativa_erro_em >= PAINEL_RECEPCAO_RETRY_SEGUNDOS):
                    st.session_state["painel_recepcao_xano_erro_em"] = monotonic()
                erro_carregamento = "Muitas tentativas. Aguarde alguns segundos antes de atualizar novamente."
            else:
                erro_carregamento = "Não foi possível carregar o resumo. Tente atualizar novamente."

    if erro_carregamento:
        st.error(erro_carregamento)
    elif carregado_em is not None:
        st.caption(f"Atualizado há {max(0, int(monotonic() - carregado_em))} s")

    if consultas is not None:
        ordenadas = sorted(consultas, key=lambda c: (_horario_consulta(c), c["id"]))
        realizadas = sum(c["situacao"] == "Realizada" for c in ordenadas)
        confirmadas = sum(c["situacao"] == "Confirmada" and _horario_consulta(c) >= agora
                          for c in ordenadas)
        situacoes_encerradas = {"Realizada", "Cancelada", "Falta"}
        proximas = [c for c in ordenadas if c["situacao"] not in situacoes_encerradas
                    and (_horario_consulta(c) >= agora or c["situacao"] == "Em atendimento")]
        proxima = proximas[0] if proximas else None
    else:
        ordenadas, realizadas, confirmadas, proxima = [], None, None, None

    indicadores = (
        ("Consultas hoje", "▣", len(ordenadas) if consultas is not None else "—"),
        ("Atendimentos", "✓", realizadas if consultas is not None else "—"),
        ("Próxima consulta", "◷", _horario_consulta(proxima).strftime("%H:%M") if proxima else "—"),
        ("Confirmadas", "✓", confirmadas if consultas is not None else "—"),
    )
    metricas = st.columns(4, gap="small")
    for indice, (rotulo, icone, valor) in enumerate(indicadores):
        with metricas[indice]:
            with st.container(key=f"metrica-xano-{indice}", border=True):
                st.markdown(f"<span class='icone-metrica'>{icone}</span>", unsafe_allow_html=True)
                st.caption(rotulo)
                st.markdown(f"<strong class='valor-metrica'>{valor}</strong>", unsafe_allow_html=True)
                detalhe = ("concluídos hoje" if indice == 1 and consultas is not None else
                           proxima["paciente_nome"] if indice == 2 and proxima else
                           "nenhuma marcada" if indice == 2 and consultas is not None else
                           "para o restante do dia" if indice == 3 else
                           "agendadas para hoje" if indice == 0 and consultas is not None else
                           "Dados indisponíveis")
                st.caption(detalhe)

    agenda, atalhos = st.columns([1.75, 1], gap="medium", vertical_alignment="top")
    with agenda:
        with st.container(key="agenda-xano-vazia", border=True):
            topo, link = st.columns([2, 1], vertical_alignment="center")
            topo.subheader("Agenda de hoje")
            topo.caption(f"{len(ordenadas)} consultas" if consultas is not None else "Resumo indisponível")
            link.button("Ver agenda completa →", key="inicio-abrir-agenda",
                        on_click=abrir_agenda, width="stretch")
            st.divider()
            if consultas is None:
                st.info("Atualize o resumo para consultar a agenda do dia.")
            elif not ordenadas:
                st.info("Nenhuma consulta para hoje.")
            else:
                for consulta in ordenadas[:5]:
                    horario = _horario_consulta(consulta)
                    hora, paciente, profissional, situacao = st.columns([0.75, 1.8, 1.5, 1])
                    hora.markdown(f"**{horario:%H:%M}**")
                    paciente.text(consulta["paciente_nome"])
                    profissional.text(consulta["profissional_nome"])
                    situacao.caption(consulta["situacao"])
                    st.divider()
    with atalhos:
        with st.container(key="cartao-acesso", border=True):
            st.subheader("Acesso rápido")
            st.caption("Acesse as áreas da clínica.")
            if pode_cadastrar_paciente:
                st.button("+  Novo paciente", on_click=pagina_paciente.abrir,
                          key="inicio-cadastrar-paciente", type="primary", width="stretch")
            st.button("▦  Visualizar agenda", on_click=abrir_agenda,
                      key="inicio-agenda-indisponivel", width="stretch")
        total = len(ordenadas) if consultas is not None else 0
        taxa = confirmadas / total if total else 0
        with st.container(key="inicio-painel-confirmadas", border=True):
            st.markdown(f"**{confirmadas if confirmadas is not None else '—'} confirmadas**")
            st.caption("para o restante do dia")
            st.progress(taxa)


def abrir_cadastro():
    limpar_formulario()
    st.session_state["pagina_equipe"] = "cadastro"


def voltar():
    limpar_formulario()
    st.session_state["pagina_equipe"] = "inicio"


def abrir_inicio():
    limpar_formulario()
    pagina_paciente.limpar()
    st.session_state["pagina_equipe"] = "inicio"


def abrir_agenda():
    st.session_state["pagina_equipe"] = "agenda"


def abrir_area_conectada(area):
    limpar_formulario()
    pagina_paciente.limpar()
    st.session_state["pagina_equipe"] = area


def abrir_nova_consulta():
    abrir_area_conectada("nova_consulta")


def _navegar_data_agenda(dias):
    dia_atual = st.session_state.get(
        "agenda_data_input", st.session_state.get("agenda_data", date.today())
    )
    novo_dia = dia_atual + timedelta(days=dias)
    st.session_state["agenda_data"] = novo_dia
    st.session_state["agenda_data_input"] = novo_dia


def _ir_para_hoje_na_agenda():
    hoje = date.today()
    st.session_state["agenda_data"] = hoje
    st.session_state["agenda_data_input"] = hoje


def _alternar_formulario_agenda(chave):
    abrir = not st.session_state.get(chave, False)
    st.session_state["agenda_nova"] = False
    st.session_state["agenda_nova_disponibilidade"] = False
    if abrir:
        st.session_state[chave] = True
        if chave == "agenda_nova":
            st.session_state["agenda-consulta-data"] = st.session_state.get(
                "agenda_data_input", st.session_state.get("agenda_data", date.today())
            )


def _data_api(dia, final=False):
    limite = datetime.combine(dia + (timedelta(days=1) if final else timedelta()), time.min,
                              tzinfo=ZoneInfo("America/Sao_Paulo"))
    return limite.isoformat(timespec="seconds")


def _atualizar_situacao_agenda(cliente, token, consulta_id):
    proxima = st.session_state[f"agenda-proxima-{consulta_id}"]
    motivo = st.session_state.get(f"agenda-motivo-{consulta_id}", "").strip()
    confirmar = st.session_state.get(f"agenda-confirmar-{consulta_id}", False)
    if proxima == "Cancelada" and not motivo:
        st.session_state["agenda_aviso"] = ("error", "Informe o motivo do cancelamento.")
        return
    if proxima == "Cancelada" and not confirmar:
        st.session_state["agenda_aviso"] = ("error", "Confirme o cancelamento antes de continuar.")
        return
    try:
        cliente.atualizar_situacao_consulta(token, consulta_id, proxima,
            motivo_cancelamento=motivo if proxima == "Cancelada" else None)
    except ErroAcesso as error:
        st.session_state["agenda_aviso"] = ("error", str(error))
    else:
        st.session_state.pop(CACHE_AGENDA_XANO, None)
        st.session_state.pop(CACHE_DISPONIBILIDADES_AGENDA, None)
        st.session_state.pop("agenda_xano_erro_em", None)
        st.session_state["agenda_aviso"] = ("success", "Situação da consulta atualizada.")


AGENDA_CACHE_TTL_SEGUNDOS = 20
AGENDA_RETRY_SEGUNDOS = 20
CACHE_AGENDA_XANO = "agenda_xano_cache"
CACHE_DISPONIBILIDADES_AGENDA = "agenda_disponibilidades_cache"


def _carregar_consultas_agenda(cliente, token, dia):
    """Reutiliza a leitura da data atual por sessão durante vinte segundos."""
    agora = monotonic()
    identidade = hashlib.sha256(token.encode("utf-8")).hexdigest()
    cache = st.session_state.get(CACHE_AGENDA_XANO)
    if not isinstance(cache, dict) or cache.get("sessao") != identidade:
        st.session_state.pop(CACHE_AGENDA_XANO, None)
        st.session_state.pop(CACHE_DISPONIBILIDADES_AGENDA, None)
        cache = {"sessao": identidade, "dias": {}}

    chave_dia = dia.isoformat()
    dias_cache = cache.get("dias")
    if not isinstance(dias_cache, dict):
        dias_cache = {}
    entrada = dias_cache.get(chave_dia)
    idade = agora - entrada.get("carregado_em", 0) if isinstance(entrada, dict) else AGENDA_CACHE_TTL_SEGUNDOS
    if (isinstance(entrada, dict) and isinstance(entrada.get("consultas"), list)
            and 0 <= idade < AGENDA_CACHE_TTL_SEGUNDOS):
        return entrada["consultas"]

    erro_em = st.session_state.get("agenda_xano_erro_em")
    if erro_em is not None and 0 <= agora - erro_em < AGENDA_RETRY_SEGUNDOS:
        raise ErroAcesso("Muitas tentativas. Aguarde alguns segundos antes de tentar novamente.", 429)

    dias_cache.pop(chave_dia, None)
    st.session_state[CACHE_AGENDA_XANO] = {"sessao": identidade, "dias": dias_cache}
    try:
        consultas = cliente.listar_consultas(
            token, inicio=_data_api(dia), fim=_data_api(dia, True)
        )
    except ErroAcesso:
        st.session_state["agenda_xano_erro_em"] = monotonic()
        raise

    carregado_em = monotonic()
    dias_cache[chave_dia] = {"consultas": consultas, "carregado_em": carregado_em}
    for chave, item in list(dias_cache.items()):
        if carregado_em - item.get("carregado_em", 0) >= AGENDA_CACHE_TTL_SEGUNDOS:
            dias_cache.pop(chave, None)
    while len(dias_cache) > 7:
        dias_cache.pop(next(iter(dias_cache)))
    st.session_state[CACHE_AGENDA_XANO] = {"sessao": identidade, "dias": dias_cache}
    st.session_state.pop("agenda_xano_erro_em", None)
    return consultas


def _carregar_disponibilidades_agenda(cliente, token, dia):
    agora = monotonic()
    identidade = hashlib.sha256(token.encode("utf-8")).hexdigest()
    cache = st.session_state.get(CACHE_DISPONIBILIDADES_AGENDA)
    if not isinstance(cache, dict) or cache.get("sessao") != identidade:
        cache = {"sessao": identidade, "dias": {}}
    dias_cache = cache.get("dias", {})
    chave_dia = dia.isoformat()
    entrada = dias_cache.get(chave_dia)
    if (isinstance(entrada, dict) and isinstance(entrada.get("disponibilidades"), list)
            and 0 <= agora - entrada.get("carregado_em", 0) < AGENDA_CACHE_TTL_SEGUNDOS):
        return entrada["disponibilidades"]
    erro_em = st.session_state.get("agenda_disponibilidades_erro_em")
    if erro_em is not None and 0 <= agora - erro_em < AGENDA_RETRY_SEGUNDOS:
        raise ErroAcesso("Muitas tentativas. Aguarde alguns segundos antes de tentar novamente.", 429)
    try:
        disponibilidades = cliente.listar_disponibilidades(
            token, inicio=_data_api(dia), fim=_data_api(dia, True)
        )
    except ErroAcesso:
        st.session_state["agenda_disponibilidades_erro_em"] = monotonic()
        raise
    dias_cache[chave_dia] = {"disponibilidades": disponibilidades, "carregado_em": monotonic()}
    for chave, item in list(dias_cache.items()):
        if monotonic() - item.get("carregado_em", 0) >= AGENDA_CACHE_TTL_SEGUNDOS:
            dias_cache.pop(chave, None)
    while len(dias_cache) > 7:
        dias_cache.pop(next(iter(dias_cache)))
    st.session_state[CACHE_DISPONIBILIDADES_AGENDA] = {"sessao": identidade, "dias": dias_cache}
    st.session_state.pop("agenda_disponibilidades_erro_em", None)
    return disponibilidades


def _renderizar_agenda(cliente, conta):
    dia_pendente = st.session_state.pop("agenda_data_pendente", None)
    if isinstance(dia_pendente, date):
        st.session_state["agenda_data"] = dia_pendente
        st.session_state["agenda_data_input"] = dia_pendente
    st.caption("ORGANIZAÇÃO DO DIA")
    st.title("Agenda")
    st.caption("Acompanhe consultas, horários e situação dos atendimentos.")
    aviso_agenda = st.session_state.pop("agenda_aviso", None)
    if aviso_agenda:
        getattr(st, aviso_agenda[0])(aviso_agenda[1])
    perfis = set(conta.perfis)
    token = st.session_state[sessao.CHAVE].token
    busca_col, data_col, status_col = st.columns([2.2, 1, 1], gap="medium")
    dia = data_col.date_input("Data", value=st.session_state.get("agenda_data", date.today()),
                              format="DD/MM/YYYY", key="agenda_data_input")
    situacao = status_col.selectbox("Situação", ["Todas", "Agendada", "Confirmada",
        "Em atendimento", "Realizada", "Cancelada", "Falta"], key="agenda_situacao")
    busca = busca_col.text_input("Buscar Paciente ou Procedimento", key="agenda_busca").strip().casefold()
    anterior, hoje, proximo = st.columns(3, vertical_alignment="center")
    anterior.button("‹", key="agenda-anterior", width="stretch",
                    help="Dia anterior",
                    on_click=_navegar_data_agenda, args=(-1,))
    hoje.button("Hoje", key="agenda-hoje", width="stretch",
                on_click=_ir_para_hoje_na_agenda)
    proximo.button("›", key="agenda-proximo", width="stretch",
                   help="Próximo dia",
                   on_click=_navegar_data_agenda, args=(1,))
    pode_agendar = bool(perfis.intersection({"administrador", "recepcionista"}))
    if pode_agendar:
        nova_consulta, novo_horario = st.columns(2, gap="small")
        nova_consulta.button("＋ Nova consulta", key="agenda-nova", type="primary", width="stretch",
                    on_click=_alternar_formulario_agenda, args=("agenda_nova",))
        novo_horario.button("＋ Novo horário", key="agenda-novo-horario", width="stretch",
                    on_click=_alternar_formulario_agenda, args=("agenda_nova_disponibilidade",))

    try:
        consultas = _carregar_consultas_agenda(cliente, token, dia)
    except ErroAcesso as error:
        if error.status in (401, 403):
            sessao.limpar(st.session_state)
            st.error(str(error))
            return
        with st.container(key="agenda-estado-erro", border=True):
            st.error(str(error) if error.status == 429
                     else "Não foi possível carregar a Agenda. Tente novamente.")
        if st.button("Tentar novamente", key="agenda-retry"):
            st.rerun()
        return

    if situacao != "Todas":
        consultas = [c for c in consultas if c["situacao"] == situacao]
    if busca:
        consultas = [c for c in consultas if busca in c["paciente_nome"].casefold()
                     or any(busca in p.casefold() for p in c["procedimentos"])]
    consultas.sort(key=lambda c: (c["inicio_em"], c["id"]))
    st.markdown(f"**{dia.strftime('%d/%m/%Y')}** · {len(consultas)} consulta(s)")

    if st.session_state.get("agenda_nova") and pode_agendar:
        _renderizar_formulario_agenda(cliente, token, dia)
    if st.session_state.get("agenda_nova_disponibilidade") and pode_agendar:
        _renderizar_formulario_disponibilidade(cliente, token, dia)
    if not consultas:
        with st.container(key="agenda-estado-vazio", border=True):
            if busca or situacao != "Todas":
                st.info("Nenhuma consulta corresponde à busca e aos filtros. Ajuste os critérios e tente novamente.")
            else:
                st.info("Nenhuma consulta agendada para este dia.")
    transicoes = {
        "Agendada": ["Confirmada", "Cancelada"],
        "Confirmada": ["Em atendimento", "Cancelada", "Falta"],
        "Em atendimento": ["Realizada"],
    }
    for consulta in consultas:
        with st.container(key=f"agenda-consulta-{consulta['id']}", border=True):
            horario = datetime.fromisoformat(consulta["inicio_em"].replace("Z", "+00:00")).astimezone(ZoneInfo("America/Sao_Paulo"))
            col_hora, col_paciente, col_prof, col_situacao = st.columns([0.8, 1.8, 1.4, 1])
            col_hora.markdown(f"**{horario:%H:%M}**")
            col_paciente.markdown(f"**{consulta['paciente_nome']}**")
            col_paciente.caption(", ".join(consulta["procedimentos"]) or "Procedimento não informado")
            col_prof.write(consulta["profissional_nome"])
            col_situacao.write(consulta["situacao"])
            permitidas = transicoes.get(consulta["situacao"], [])
            if "profissional" not in perfis:
                permitidas = [s for s in permitidas if s in {"Confirmada", "Cancelada"}]
            pode_atualizar = bool(perfis.intersection({"profissional", "administrador", "recepcionista"}))
            if permitidas and pode_atualizar:
                acao_col, motivo_col, enviar_col = st.columns([1, 2, 1])
                proxima = acao_col.selectbox("Alterar situação", permitidas,
                                             key=f"agenda-proxima-{consulta['id']}")
                motivo_col.text_input("Motivo do cancelamento", max_chars=1000,
                    key=f"agenda-motivo-{consulta['id']}", disabled=proxima != "Cancelada")
                motivo_col.checkbox("Confirmo o cancelamento", key=f"agenda-confirmar-{consulta['id']}",
                    disabled=proxima != "Cancelada")
                enviar_col.button("Atualizar", key=f"agenda-atualizar-{consulta['id']}", width="stretch",
                    on_click=_atualizar_situacao_agenda, args=(cliente, token, consulta["id"]))

    _renderizar_disponibilidades_agenda(cliente, token, dia, perfis)


def _renderizar_disponibilidades_agenda(cliente, token, dia, perfis):
    pode_gerenciar = bool(perfis.intersection({"profissional", "administrador", "recepcionista"}))
    st.subheader("Horários da agenda")
    try:
        disponibilidades = _carregar_disponibilidades_agenda(cliente, token, dia)
    except ErroAcesso as error:
        if error.status in (401, 403):
            sessao.limpar(st.session_state)
        st.error(str(error) if error.status in (401, 403, 429)
                 else "Não foi possível carregar os horários da Agenda.")
        return

    if not disponibilidades:
        st.info("Nenhum horário futuro disponível ou bloqueado nesta data.")
        return

    fuso = ZoneInfo("America/Sao_Paulo")
    for disponibilidade in disponibilidades:
        inicio = datetime.fromisoformat(disponibilidade["inicio"].replace("Z", "+00:00")).astimezone(fuso)
        fim = datetime.fromisoformat(disponibilidade["fim"].replace("Z", "+00:00")).astimezone(fuso)
        rotulo_situacao = "Bloqueado" if disponibilidade["situacao"] == "bloqueado" else "Disponível"
        with st.container(key=f"agenda-horario-{disponibilidade['id']}", border=True):
            st.markdown(f"**{inicio:%H:%M}–{fim:%H:%M}** · {disponibilidade['profissional_nome']}")
            st.caption(rotulo_situacao)
            if not pode_gerenciar:
                continue
            col_editar, col_situacao = st.columns([1, 1], gap="small")
            expandir_edicao = st.session_state.get(f"agenda-editar-{disponibilidade['id']}", False)
            if col_editar.button("Editar horário" if not expandir_edicao else "Fechar edição",
                                 key=f"agenda-horario-editar-toggle-{disponibilidade['id']}", width="stretch"):
                st.session_state[f"agenda-editar-{disponibilidade['id']}"] = not expandir_edicao
                st.rerun()
            novo_estado = "disponivel" if disponibilidade["situacao"] == "bloqueado" else "bloqueado"
            acao_estado = "Desbloquear" if novo_estado == "disponivel" else "Bloquear"
            if col_situacao.button(acao_estado, key=f"agenda-horario-situacao-{disponibilidade['id']}",
                                   width="stretch"):
                try:
                    cliente.atualizar_disponibilidade(
                        token, disponibilidade["id"], situacao=novo_estado
                    )
                    st.session_state.pop(CACHE_AGENDA_XANO, None)
                    st.session_state.pop(CACHE_DISPONIBILIDADES_AGENDA, None)
                    mensagem = "Horário desbloqueado." if novo_estado == "disponivel" else "Horário bloqueado."
                    st.session_state["agenda_aviso"] = ("success", mensagem)
                    st.rerun()
                except ErroAcesso as error:
                    st.error(str(error))
            if expandir_edicao:
                with st.form(f"agenda-horario-form-{disponibilidade['id']}", border=True):
                    data = st.date_input("Data", value=inicio.date(), format="DD/MM/YYYY",
                                         key=f"agenda-horario-data-{disponibilidade['id']}")
                    col_inicio, col_fim = st.columns(2, gap="small")
                    hora_inicio = col_inicio.time_input("Início", value=inicio.time().replace(tzinfo=None),
                                                        key=f"agenda-horario-inicio-{disponibilidade['id']}")
                    hora_fim = col_fim.time_input("Fim", value=fim.time().replace(tzinfo=None),
                                                  key=f"agenda-horario-fim-{disponibilidade['id']}")
                    salvar = st.form_submit_button("Salvar intervalo", type="primary")
                if salvar:
                    inicio_novo = datetime.combine(data, hora_inicio, tzinfo=fuso)
                    fim_novo = datetime.combine(data, hora_fim, tzinfo=fuso)
                    if inicio_novo <= datetime.now(fuso):
                        st.error("O início do horário precisa ser futuro.")
                    elif fim_novo <= inicio_novo:
                        st.error("O horário final deve ser posterior ao horário inicial.")
                    else:
                        try:
                            cliente.atualizar_disponibilidade(
                                token, disponibilidade["id"],
                                inicio=inicio_novo.isoformat(timespec="seconds"),
                                fim=fim_novo.isoformat(timespec="seconds"),
                            )
                            st.session_state.pop(CACHE_AGENDA_XANO, None)
                            st.session_state.pop(CACHE_DISPONIBILIDADES_AGENDA, None)
                            st.session_state[f"agenda-editar-{disponibilidade['id']}"] = False
                            st.session_state["agenda_aviso"] = ("success", "Horário atualizado.")
                            st.rerun()
                        except ErroAcesso as error:
                            st.error(str(error))


def _renderizar_formulario_agenda(cliente, token, dia):
    try:
        opcoes = cliente.listar_opcoes_agenda(token)
    except ErroAcesso as error:
        st.error(str(error) if error.status in (401, 403, 429) else "Não foi possível carregar as opções de agendamento.")
        return
    if not opcoes["pacientes"] or not opcoes["profissionais"]:
        st.info("Cadastre Pacientes e Profissionais ativos antes de agendar.")
        return
    with st.container(border=True):
        st.subheader("Nova consulta")
        pacientes = {i["id"]: i["nome"] for i in opcoes["pacientes"]}
        profissionais = {i["id"]: i["nome"] for i in opcoes["profissionais"]}
        procedimentos = {i["id"]: i["nome"] for i in opcoes["procedimentos"]}
        profissional_id = st.selectbox("Profissional", list(profissionais), format_func=profissionais.get, key="agenda-profissional")
        data_consulta = st.date_input("Data da consulta", value=dia, format="DD/MM/YYYY",
                                      key="agenda-consulta-data")
        inicio, fim = _data_api(data_consulta), _data_api(data_consulta, True)
        try:
            disponibilidades = cliente.listar_disponibilidades(token, profissional_id, inicio, fim)
        except ErroAcesso as error:
            st.error("Não foi possível carregar os horários disponíveis." if error.status not in (401, 403) else str(error))
            disponibilidades = []
        horarios = {d["id"]: f"{datetime.fromisoformat(d['inicio'].replace('Z', '+00:00')).astimezone(ZoneInfo('America/Sao_Paulo')):%H:%M} – {datetime.fromisoformat(d['fim'].replace('Z', '+00:00')).astimezone(ZoneInfo('America/Sao_Paulo')):%H:%M}" for d in disponibilidades}
        if not horarios:
            st.info("Nenhum horário disponível para este profissional nesta data.")
        with st.form("agenda-form-nova-consulta"):
            paciente_id = st.selectbox("Paciente", list(pacientes), format_func=pacientes.get, key="agenda-paciente")
            disponibilidade_id = st.selectbox("Horário disponível", list(horarios), format_func=horarios.get,
                index=None, placeholder="Selecione um horário", key="agenda-disponibilidade")
            procedimento_ids = st.multiselect("Procedimentos (opcional)", list(procedimentos),
                format_func=procedimentos.get, key="agenda-procedimentos")
            motivo = st.text_area("Observação administrativa (opcional)", max_chars=1000, key="agenda-motivo-nova")
            enviar, fechar = st.columns(2)
            enviar_consulta = enviar.form_submit_button("Agendar consulta", type="primary", disabled=not horarios)
            cancelar_form = fechar.form_submit_button("Fechar")
    if cancelar_form:
        st.session_state["agenda_nova"] = False
        st.rerun()
    if enviar_consulta:
        if disponibilidade_id is None:
            st.error("Selecione um horário disponível.")
            return
        try:
            cliente.agendar_consulta(token, paciente_id, disponibilidade_id, procedimento_ids,
                                     motivo=motivo.strip() or None)
            st.session_state.pop(CACHE_AGENDA_XANO, None)
            st.session_state.pop(CACHE_DISPONIBILIDADES_AGENDA, None)
            st.session_state["agenda_nova"] = False
            st.session_state["agenda_data_pendente"] = data_consulta
            st.session_state["agenda_aviso"] = ("success", "Consulta agendada.")
            st.rerun()
        except ErroAcesso as error:
            st.error(str(error))


def _renderizar_formulario_disponibilidade(cliente, token, dia):
    try:
        opcoes = cliente.listar_opcoes_agenda(token)
    except ErroAcesso as error:
        st.error(str(error) if error.status in (401, 403, 429)
                 else "Não foi possível carregar os Profissionais.")
        return
    profissionais = {item["id"]: item["nome"] for item in opcoes["profissionais"]}
    if not profissionais:
        st.info("Nenhum Profissional ativo disponível para cadastrar horário.")
        return

    fuso = ZoneInfo("America/Sao_Paulo")
    agora = datetime.now(fuso)
    data_padrao = max(dia, agora.date())
    inicio_padrao = time(9, 0)
    if data_padrao == agora.date():
        proximo_horario = agora.replace(second=0, microsecond=0) + timedelta(minutes=15)
        minuto_arredondado = ((proximo_horario.minute + 14) // 15) * 15
        if minuto_arredondado == 60:
            proximo_horario = proximo_horario.replace(minute=0) + timedelta(hours=1)
        else:
            proximo_horario = proximo_horario.replace(minute=minuto_arredondado)
        if proximo_horario.date() != data_padrao:
            data_padrao += timedelta(days=1)
        else:
            inicio_padrao = proximo_horario.time()
    if not st.session_state.get("agenda_disponibilidade_padroes_iniciados"):
        st.session_state["agenda-disponibilidade-data"] = data_padrao
        st.session_state["agenda-disponibilidade-inicio"] = inicio_padrao
        st.session_state["agenda-disponibilidade-fim"] = (
            datetime.combine(data_padrao, inicio_padrao) + timedelta(hours=1)
        ).time()
        st.session_state["agenda_disponibilidade_padroes_iniciados"] = True

    with st.form("agenda-form-nova-disponibilidade", border=True):
        st.subheader("Novo horário disponível")
        profissional_id = st.selectbox(
            "Profissional", list(profissionais), format_func=profissionais.get,
            key="agenda-disponibilidade-profissional",
        )
        data = st.date_input("Data do horário", value=st.session_state["agenda-disponibilidade-data"], format="DD/MM/YYYY",
                             key="agenda-disponibilidade-data")
        inicio_coluna, fim_coluna = st.columns(2, gap="small")
        hora_inicio = inicio_coluna.time_input(
            "Horário inicial", value=st.session_state["agenda-disponibilidade-inicio"], key="agenda-disponibilidade-inicio",
        )
        hora_fim = fim_coluna.time_input(
            "Horário final", value=st.session_state["agenda-disponibilidade-fim"], key="agenda-disponibilidade-fim",
        )
        salvar, fechar = st.columns(2)
        enviar = salvar.form_submit_button("Cadastrar horário", type="primary")
        cancelar = fechar.form_submit_button("Fechar")

    if cancelar:
        st.session_state["agenda_nova_disponibilidade"] = False
        st.session_state["agenda_disponibilidade_padroes_iniciados"] = False
        st.rerun()
    if not enviar:
        return

    inicio = datetime.combine(data, hora_inicio, tzinfo=fuso)
    fim = datetime.combine(data, hora_fim, tzinfo=fuso)
    agora = datetime.now(fuso)
    if inicio <= agora:
        st.error(
            "O início precisa ser futuro. O formulário recebeu "
            f"{inicio:%d/%m/%Y às %H:%M}; agora são {agora:%d/%m/%Y às %H:%M}."
        )
        return
    if fim <= inicio:
        st.error("O horário final deve ser posterior ao horário inicial.")
        return
    try:
        cliente.criar_disponibilidade(
            token, profissional_id, inicio.isoformat(timespec="seconds"),
            fim.isoformat(timespec="seconds"),
        )
        st.session_state.pop(CACHE_AGENDA_XANO, None)
        st.session_state.pop(CACHE_DISPONIBILIDADES_AGENDA, None)
        st.session_state["agenda_nova_disponibilidade"] = False
        st.session_state["agenda_disponibilidade_padroes_iniciados"] = False
        st.session_state["agenda_aviso"] = (
            "success", "Horário cadastrado. Ele já pode ser usado em uma nova consulta.",
        )
        st.rerun()
    except ErroAcesso as error:
        st.error(str(error))


def solicitar_cadastro():
    if st.session_state.get("cad_processando"):
        return
    senha = st.session_state.get("cad_senha", "")
    confirmacao = st.session_state.get("cad_confirmacao", "")
    st.session_state["cad_senha"] = ""
    st.session_state["cad_confirmacao"] = ""
    if senha != confirmacao:
        st.session_state["cad_aviso"] = ("error", "A confirmação da senha não confere.")
        return
    st.session_state["cad_pendente"] = {
        "nome": st.session_state.get("cad_nome", ""),
        "email": st.session_state.get("cad_email", ""),
        "senha": senha,
        "cro": st.session_state.get("cad_cro", ""),
        "especialidade_id": st.session_state.get("cad_especialidade"),
    }
    st.session_state["cad_processando"] = True


def renderizar_cadastro(cliente):
    restaurar = st.session_state.pop("cad_restaurar", {})
    for campo, valor in restaurar.items():
        st.session_state["cad_" + campo] = valor
    if st.session_state.pop("cad_limpar", False):
        limpar_formulario()
        st.success("Profissional cadastrado. Ele já pode entrar pelo login da equipe.")
    token = st.session_state[sessao.CHAVE].token
    try:
        especialidades = listar_especialidades_sessao(cliente, token)
    except ErroAcesso as error:
        limpar_formulario()
        if error.status in (401, 403):
            sessao.limpar(st.session_state)
            st.session_state["aviso"] = ("error", str(error))
            st.rerun()
        st.error("Não foi possível carregar as especialidades. Tente novamente em instantes.")
        st.button("Tentar novamente", on_click=limpar_formulario)
        return
    opcoes = {item["id"]: item["nome"] for item in especialidades}
    if not opcoes:
        st.info("Nenhuma especialidade disponível. Configure uma especialidade ativa no Xano.")
    ocupado = st.session_state.get("cad_processando", False)
    mensagem = st.session_state.pop("cad_aviso", None)
    if mensagem:
        getattr(st, mensagem[0])(mensagem[1])
    with st.form("cadastro_profissional", border=False):
        st.text_input("Nome completo", key="cad_nome", max_chars=120,
                      placeholder="Nome do profissional", disabled=ocupado)
        especialidade, cro = st.columns(2, gap="medium")
        especialidade.selectbox("Especialidade", options=list(opcoes), index=None,
                                 format_func=lambda value: opcoes.get(value, ""),
                                 placeholder="Ex.: Ortodontia", key="cad_especialidade",
                                 disabled=ocupado or not opcoes)
        cro.text_input("CRO", key="cad_cro", placeholder="CRO-SP 00000", max_chars=32,
                       disabled=ocupado)
        st.text_input("E-mail do profissional", key="cad_email", max_chars=254,
                      placeholder="profissional@clinica.com", disabled=ocupado)
        senha, confirmacao = st.columns(2, gap="medium")
        senha.text_input("Senha inicial", key="cad_senha", type="password", max_chars=128,
                         help="De 12 a 128 caracteres.", disabled=ocupado)
        confirmacao.text_input("Confirmar senha", key="cad_confirmacao", type="password",
                               max_chars=128, disabled=ocupado)
        _, cancelar, _, enviar = st.columns([1, 0.8, 0.15, 1.4], gap="small",
                                            vertical_alignment="center")
        cancelar.form_submit_button("Voltar", on_click=voltar, disabled=ocupado, width="stretch")
        enviar.form_submit_button("Cadastrando…" if ocupado else "Cadastrar profissional",
                                  type="primary", width="stretch",
                                  on_click=solicitar_cadastro, disabled=ocupado or not opcoes)
    if ocupado:
        dados = st.session_state.pop("cad_pendente", None)
        try:
            if dados:
                with st.spinner("Cadastrando profissional…"):
                    cliente.cadastrar_profissional(token, **dados)
                st.session_state["cad_limpar"] = True
        except ErroAcesso as error:
            if error.status in (401, 403):
                sessao.limpar(st.session_state)
                st.session_state["aviso"] = ("error", str(error))
            else:
                st.session_state["cad_aviso"] = ("error", str(error))
                if dados:
                    st.session_state["cad_restaurar"] = {
                        "nome": dados["nome"], "email": dados["email"],
                        "cro": dados["cro"], "especialidade": dados["especialidade_id"],
                    }
        finally:
            if dados:
                dados.clear()
            if sessao.CHAVE in st.session_state:
                st.session_state["cad_processando"] = False
        st.rerun()


def renderizar_cadastro_modal(cliente):
    with st.container(key="modal-profissional"):
        cabecalho, fechar = st.columns([8, 1], vertical_alignment="center")
        cabecalho.markdown("### Novo profissional")
        cabecalho.caption("Cadastre um dentista e associe uma especialidade ativa.")
        if fechar.button("×", key="cad-fechar-modal", help="Fechar cadastro"):
            voltar()
            st.rerun()
        st.divider()
        renderizar_cadastro(cliente)


def _carregar_resumo_painel_administrador(cliente, credencial, dia):
    """Cacheia as duas leituras administrativas por sessao, dia e vinte segundos."""
    agora = monotonic()
    if credencial.expira_em <= datetime.now(ZoneInfo("UTC")):
        st.session_state.pop(CACHE_PAINEL_ADMIN, None)
        raise ErroAcesso("Sua sessão expirou. Entre novamente para consultar o resumo.", 401)

    identidade = hashlib.sha256(credencial.token.encode("utf-8")).hexdigest()
    erro_em = st.session_state.get("painel_administrativo_xano_erro_em")
    if erro_em is not None and 0 <= agora - erro_em < PAINEL_ADMIN_RETRY_SEGUNDOS:
        raise ErroAcesso("Muitas tentativas. Aguarde alguns segundos antes de tentar novamente.", 429)

    cache = st.session_state.get(CACHE_PAINEL_ADMIN)
    idade = agora - cache.get("carregado_em", 0) if isinstance(cache, dict) else PAINEL_ADMIN_CACHE_TTL_SEGUNDOS
    if (isinstance(cache, dict) and cache.get("sessao") == identidade
            and cache.get("dia") == dia
            and 0 <= idade < PAINEL_ADMIN_CACHE_TTL_SEGUNDOS
            and isinstance(cache.get("consultas"), list)
            and type(cache.get("pacientes_ativos")) is int):
        return cache["consultas"], cache["pacientes_ativos"]

    st.session_state.pop(CACHE_PAINEL_ADMIN, None)
    try:
        consultas = cliente.listar_consultas(
            credencial.token, inicio=_data_api(dia), fim=_data_api(dia, True)
        )
        opcoes = cliente.listar_opcoes_agenda(credencial.token)
        pacientes_ativos = len(opcoes["pacientes"])
    except (ErroAcesso, KeyError, TypeError, ValueError):
        st.session_state["painel_administrativo_xano_erro_em"] = monotonic()
        raise

    carregado_em = monotonic()
    st.session_state.pop("painel_administrativo_xano_erro_em", None)
    st.session_state[CACHE_PAINEL_ADMIN] = {
        "sessao": identidade,
        "dia": dia,
        "consultas": consultas,
        "pacientes_ativos": pacientes_ativos,
        "carregado_em": carregado_em,
    }
    return consultas, pacientes_ativos


def _renderizar_painel_administrador(cliente, conta, pode_cadastrar_paciente, pode_agendar):
    """Resumo diário da Administração baseado nos contratos existentes do Xano."""
    fuso = ZoneInfo("America/Sao_Paulo")
    agora = datetime.now(fuso)
    dia = agora.date()
    dias = ("SEGUNDA-FEIRA", "TERÇA-FEIRA", "QUARTA-FEIRA", "QUINTA-FEIRA",
            "SEXTA-FEIRA", "SÁBADO", "DOMINGO")
    meses = ("JANEIRO", "FEVEREIRO", "MARÇO", "ABRIL", "MAIO", "JUNHO",
             "JULHO", "AGOSTO", "SETEMBRO", "OUTUBRO", "NOVEMBRO", "DEZEMBRO")
    st.caption(f"{dias[dia.weekday()]}, {dia.day} DE {meses[dia.month - 1]}")
    titulo, acao = st.columns([3, 1], vertical_alignment="center")
    primeiro_nome = conta.nome.split()[0] if conta.nome.strip() else "equipe"
    titulo.title(f"Olá, {primeiro_nome}! 👋")
    titulo.caption("Aqui está um resumo da clínica hoje.")
    consulta_integrada = navegacao.modulo_xano_disponivel("nova_consulta")
    if pode_agendar:
        acao.button(
            "+ Nova consulta", key="inicio-nova-consulta",
            on_click=abrir_nova_consulta if consulta_integrada else None,
            disabled=not consulta_integrada, width="stretch",
            help=None if consulta_integrada else "A tela Nova Consulta ainda não está integrada ao Xano.",
        )

    credencial = st.session_state.get(sessao.CHAVE)
    consultas = pacientes_ativos = None
    erro = None
    if credencial is None:
        erro = "Sua sessão expirou. Entre novamente para consultar o resumo."
    else:
        try:
            with st.spinner("Carregando o resumo da clínica…"):
                consultas, pacientes_ativos = _carregar_resumo_painel_administrador(
                    cliente, credencial, dia
                )
        except ErroAcesso as error:
            consultas = pacientes_ativos = None
            if error.status == 401:
                sessao.limpar(st.session_state)
                erro = "Sua sessão expirou. Entre novamente para consultar o resumo."
            elif error.status == 403:
                erro = "Sua Conta de Acesso não tem permissão para consultar este resumo."
            elif error.status == 429:
                erro = "Muitas tentativas. Aguarde um pouco e tente novamente."
            else:
                erro = "Não foi possível carregar o resumo da clínica. Tente novamente."
        except (KeyError, TypeError, ValueError):
            consultas = pacientes_ativos = None
            erro = "Não foi possível carregar o resumo da clínica. Tente novamente."

    if erro:
        st.error(erro)
        if st.button("Tentar novamente", key="inicio-admin-retry"):
            st.rerun()

    ordenadas = []
    realizadas = confirmadas = None
    proxima = None
    if consultas is not None:
        try:
            ordenadas = sorted(consultas, key=lambda consulta: (_horario_consulta(consulta), consulta["id"]))
            realizadas = sum(consulta["situacao"] in {"Realizada", "Concluída"} for consulta in ordenadas)
            confirmadas = sum(consulta["situacao"] == "Confirmada" and _horario_consulta(consulta) >= agora
                              for consulta in ordenadas)
            encerradas = {"Realizada", "Concluída", "Cancelada", "Falta"}
            proxima = next((consulta for consulta in ordenadas
                            if consulta["situacao"] not in encerradas
                            and (_horario_consulta(consulta) >= agora
                                 or consulta["situacao"] == "Em atendimento")), None)
        except (KeyError, TypeError, ValueError):
            consultas = pacientes_ativos = None
            ordenadas, realizadas, confirmadas, proxima = [], None, None, None
            st.error("Não foi possível carregar o resumo da clínica. Tente novamente.")
            if st.button("Tentar novamente", key="inicio-admin-retry-dados"):
                st.rerun()

    indicadores = (
        ("Consultas hoje", "□", len(ordenadas) if consultas is not None else "—"),
        ("Atendimentos", "✓", realizadas if consultas is not None else "—"),
        ("Pacientes ativos", "♙", pacientes_ativos if pacientes_ativos is not None else "—"),
        ("Próxima consulta", "◷", _horario_consulta(proxima).strftime("%H:%M") if proxima else "—"),
    )
    metricas = st.columns(4, gap="small")
    for indice, (rotulo, icone, valor) in enumerate(indicadores):
        with metricas[indice]:
            with st.container(key=f"metrica-admin-{indice}", border=True):
                st.markdown(f"<span class='icone-metrica'>{icone}</span>", unsafe_allow_html=True)
                st.caption(rotulo)
                st.markdown(f"<strong class='valor-metrica'>{valor}</strong>", unsafe_allow_html=True)
                detalhe = (
                    "concluídos hoje" if indice == 1 and consultas is not None else
                    "cadastros no sistema" if indice == 2 and pacientes_ativos is not None else
                    proxima["paciente_nome"] if indice == 3 and proxima else
                    "nenhuma marcada" if indice == 3 and consultas is not None else
                    "agendadas para hoje" if indice == 0 and consultas is not None else
                    "Dados indisponíveis"
                )
                st.caption(detalhe)

    agenda, atalhos = st.columns([1.75, 1], gap="medium", vertical_alignment="top")
    with agenda:
        with st.container(key="agenda-admin-hoje", border=True):
            topo, link = st.columns([2, 1], vertical_alignment="center")
            topo.subheader("Agenda de hoje")
            topo.caption(f"{len(ordenadas)} consultas" if consultas is not None else "Resumo indisponível")
            link.button("Ver agenda completa →", key="inicio-abrir-agenda",
                        on_click=abrir_agenda, width="stretch")
            st.divider()
            if consultas is None:
                st.info("Atualize o resumo para consultar a agenda do dia.")
            elif not ordenadas:
                st.info("Nenhuma consulta para hoje.")
            else:
                for consulta in ordenadas[:5]:
                    horario = _horario_consulta(consulta)
                    hora, paciente, profissional, situacao = st.columns([0.75, 1.8, 1.5, 1])
                    hora.markdown(f"**{horario:%H:%M}**")
                    paciente.text(consulta["paciente_nome"])
                    profissional.text(consulta["profissional_nome"])
                    situacao.caption("Realizada" if consulta["situacao"] == "Concluída"
                                     else consulta["situacao"])
                    st.divider()
    with atalhos:
        with st.container(key="cartao-acesso-admin", border=True):
            st.subheader("Acesso rápido")
            st.caption("Acesse as áreas da clínica.")
            if pode_cadastrar_paciente:
                st.button("＋  Novo paciente", on_click=pagina_paciente.abrir,
                          key="inicio-cadastrar-paciente", type="primary", width="stretch")
            if navegacao.pode_acessar(conta.perfis, "prontuarios"):
                prontuario_integrado = navegacao.modulo_xano_disponivel("prontuarios")
                st.button("▤  Abrir prontuário", key="inicio-prontuario-indisponivel",
                          on_click=(lambda: abrir_area_conectada("prontuarios")) if prontuario_integrado else None,
                          disabled=not prontuario_integrado, width="stretch",
                          help=None if prontuario_integrado else "A listagem de Prontuários ainda não está integrada ao Xano.")
            st.button("▦  Visualizar agenda", on_click=abrir_agenda,
                      key="inicio-agenda-indisponivel", width="stretch")
            if "administrador" in conta.perfis:
                st.button("＋  Novo profissional", on_click=abrir_cadastro,
                          key="inicio-cadastrar-profissional", width="stretch")
        total = len(ordenadas) if consultas is not None else 0
        taxa = confirmadas / total if total else 0
        with st.container(key="inicio-admin-confirmadas", border=True):
            st.markdown(f"**{confirmadas if confirmadas is not None else '—'} confirmadas**")
            st.caption("para o restante do dia")
            st.progress(taxa)


def renderizar_inicio(cliente, conta, administrador, pode_cadastrar_paciente, pode_agendar):
    if "recepcionista" in conta.perfis:
        _renderizar_painel_recepcao(cliente, conta, pode_cadastrar_paciente, pode_agendar)
        return
    if "profissional" in conta.perfis:
        from . import painel_profissional
        painel_profissional.renderizar(cliente, conta)
        return
    if administrador:
        _renderizar_painel_administrador(cliente, conta, pode_cadastrar_paciente, pode_agendar)
        return
    dia = date.today()
    dias = ("SEGUNDA-FEIRA", "TERÇA-FEIRA", "QUARTA-FEIRA", "QUINTA-FEIRA",
            "SEXTA-FEIRA", "SÁBADO", "DOMINGO")
    meses = ("JANEIRO", "FEVEREIRO", "MARÇO", "ABRIL", "MAIO", "JUNHO",
             "JULHO", "AGOSTO", "SETEMBRO", "OUTUBRO", "NOVEMBRO", "DEZEMBRO")
    st.caption(f"{dias[dia.weekday()]}, {dia.day} DE {meses[dia.month - 1]}")
    titulo, acao = st.columns([3, 1], vertical_alignment="center")
    primeiro_nome = conta.nome.split()[0] if conta.nome.strip() else "equipe"
    titulo.title(f"Olá, {primeiro_nome}! 👋")
    titulo.caption("Aqui está um resumo da clínica hoje.")
    consulta_integrada = navegacao.modulo_xano_disponivel("nova_consulta")
    if pode_agendar:
        acao.button(
            "＋ Nova consulta", key="inicio-nova-consulta",
            on_click=abrir_nova_consulta if consulta_integrada else None,
            disabled=not consulta_integrada, width="stretch",
            help=None if consulta_integrada else "A tela Nova Consulta ainda não está integrada ao Xano.",
        )

    indicadores = (
        ("Consultas hoje", "▢"), ("Atendimentos", "✓"),
        ("Pacientes ativos", "♙"), ("Próxima consulta", "◷"),
    )
    metricas = st.columns(4, gap="small")
    for indice, (rotulo, icone) in enumerate(indicadores):
        with metricas[indice]:
            with st.container(key=f"metrica-xano-{indice}", border=True):
                st.markdown(f"<span class='icone-metrica'>{icone}</span>", unsafe_allow_html=True)
                st.caption(rotulo)
                st.markdown("<strong class='valor-metrica'>—</strong>", unsafe_allow_html=True)
                st.caption("Dados indisponíveis")

    agenda, atalhos = st.columns([1.75, 1], gap="medium", vertical_alignment="top")
    with agenda:
        with st.container(key="agenda-xano-vazia", border=True):
            titulo_agenda, abrir_agenda = st.columns([2, 1], vertical_alignment="center")
            titulo_agenda.subheader("Agenda de hoje")
            abrir_agenda.caption("Hoje")
            st.divider()
            st.info("Nenhuma consulta disponível para exibir.")
    with atalhos:
        with st.container(key="cartao-acesso", border=True):
            st.subheader("Acesso rápido")
            st.caption("Acesse as áreas da clínica.")
            if pode_cadastrar_paciente:
                st.button("＋  Novo paciente", on_click=pagina_paciente.abrir,
                          key="inicio-cadastrar-paciente", type="primary", width="stretch")
            if navegacao.pode_acessar(conta.perfis, "prontuarios"):
                prontuario_integrado = navegacao.modulo_xano_disponivel("prontuarios")
                st.button("▤  Abrir prontuário", key="inicio-prontuario-indisponivel",
                          on_click=(lambda: abrir_area_conectada("prontuarios")) if prontuario_integrado else None,
                          disabled=not prontuario_integrado, width="stretch",
                          help=None if prontuario_integrado else "A listagem de Prontuários ainda não está integrada ao Xano.")
            st.button("▦  Visualizar agenda", key="inicio-agenda-indisponivel",
                      disabled=True, width="stretch",
                      help="A agenda ainda não está integrada ao Xano.")
            if administrador:
                st.button("＋  Novo profissional", on_click=abrir_cadastro,
                          key="inicio-cadastrar-profissional", width="stretch")
            if not administrador and not pode_cadastrar_paciente:
                st.info("Seu acesso à equipe está ativo.")


def renderizar(conta, cliente):
    if cliente.configuracao.modo_demonstracao:
        from . import paginas_demo
        paginas_demo.renderizar(conta, cliente)
        return

    perfis = set(conta.perfis)
    if st.session_state.pop("pac_sucesso", False):
        st.success("Paciente cadastrado com prontuÃ¡rio vazio. Este cadastro nÃ£o cria login.")
    paciente_exclusivo = perfis == {"paciente"}
    administrador = "administrador" in perfis
    pode_cadastrar_paciente = (cliente.configuracao.cadastro_paciente_habilitado
                              and bool(set(conta.perfis) & {"administrador", "recepcionista"}))
    if not administrador:
        limpar_formulario()
        if st.session_state.get("pagina_equipe") == "cadastro":
            st.session_state.pop("pagina_equipe", None)
    if not pode_cadastrar_paciente:
        pagina_paciente.limpar()
        if st.session_state.get("pagina_equipe") == "paciente":
            st.session_state.pop("pagina_equipe", None)
    pagina_padrao = "prontuarios" if paciente_exclusivo else "inicio"
    pagina = st.session_state.get("pagina_equipe", pagina_padrao)
    if paciente_exclusivo and pagina != "prontuarios":
        pagina = pagina_padrao
        st.session_state["pagina_equipe"] = pagina
    elif pagina not in {"inicio", "agenda", "cadastro", "paciente"} and (
            not navegacao.pode_acessar(conta.perfis, pagina)
            or not navegacao.modulo_xano_disponivel(pagina)):
        pagina = pagina_padrao
        st.session_state["pagina_equipe"] = pagina
    ocupado = (st.session_state.get("cad_processando", False)
               or st.session_state.get("pac_processando", False))
    with st.container(key="layout-equipe"):
        menu, conteudo = st.columns([0.205, 0.795], gap="medium", vertical_alignment="top")
        with menu:
            with st.container(key="menu-equipe", border=True):
                renderizar_marca_menu()
                if not paciente_exclusivo:
                    st.button("Visão geral", on_click=abrir_inicio, key="menu-inicio",
                              disabled=ocupado, width="stretch")
                for area in navegacao.areas_visiveis(
                    conta.perfis, modo_demonstracao=False,
                    cadastro_paciente_habilitado=cliente.configuracao.cadastro_paciente_habilitado,
                ):
                    if area["chave"] == "agenda":
                        st.button(area["rotulo"], key="menu-agenda", on_click=abrir_agenda,
                                  disabled=ocupado, width="stretch")
                    elif area["chave"] != "inicio":
                        st.button(
                            area["rotulo"],
                            key=(f"menu-{area['chave']}" if area["disponivel"]
                                 else f"menu-indisponivel-{area['chave']}"),
                            on_click=(lambda chave=area["chave"]: abrir_area_conectada(chave))
                            if area["disponivel"] else None,
                            disabled=ocupado or not area["disponivel"], width="stretch",
                            help=None if area["disponivel"]
                            else "A integração desta área com o Xano ainda não está disponível.",
                        )
                st.caption("Cadastros integrados")
                if pode_cadastrar_paciente:
                    st.button("Cadastrar paciente", on_click=pagina_paciente.abrir,
                              key="menu-cadastrar-paciente", disabled=ocupado or pagina == "paciente",
                              width="stretch")
                if administrador:
                    st.button("Cadastrar profissional", on_click=abrir_cadastro,
                              key="menu-cadastrar-profissional", disabled=ocupado or pagina == "cadastro",
                              width="stretch")
                st.divider()
                st.caption("SEU ACESSO")
                st.text(conta.nome)
                st.caption(" · ".join(ROTULOS[p] for p in conta.perfis))
                if st.button("Sair", key="sair", width="stretch", disabled=ocupado):
                    with st.spinner("Encerrando seu acesso…"):
                        mensagem = sessao.sair(st.session_state, cliente)
                    st.session_state["aviso"] = ("info", mensagem)
                    st.rerun()
        with conteudo:
            with st.container(key="conteudo-equipe", border=True):
                if pagina == "agenda":
                    renderizar_topbar(conta, "agenda")
                    _renderizar_agenda(cliente, conta)
                elif pagina == "inicio":
                    renderizar_topbar(conta, "inicio")
                    renderizar_inicio(cliente, conta, administrador, pode_cadastrar_paciente,
                                      bool(set(conta.perfis) & navegacao.PERFIS_NOVA_CONSULTA))
                else:
                    renderizar_topbar(conta, pagina)
                    modulo = navegacao.carregar_modulo_xano(pagina)
                    if modulo and callable(getattr(modulo, "renderizar", None)):
                        modulo.renderizar(cliente, conta)
                    else:
                        st.info("A integração desta área com o Xano ainda não está disponível.")
    if administrador and pagina == "cadastro":
        renderizar_cadastro_modal(cliente)
    elif pode_cadastrar_paciente and pagina == "paciente":
        pagina_paciente.renderizar_modal(cliente)


def renderizar_topbar(conta, pagina):
    """Faixa superior inspirada no breadcrumb e perfil das referências."""
    titulos = {
        "inicio": "Visão geral", "agenda": "Agenda", "pacientes": "Pacientes",
        "profissionais": "Profissionais", "prontuarios": "Prontuários",
        "procedimentos": "Procedimentos", "paciente": "Novo paciente",
        "cadastro": "Novo profissional", "nova_consulta": "Nova consulta",
    }
    with st.container(key="topbar-equipe"):
        breadcrumb, perfil = st.columns([3, 1], vertical_alignment="center")
        breadcrumb.caption(f"Sorriso+  /  {titulos.get(pagina, 'Equipe')}")
        nome_perfil = " · ".join("Dentista" if p == "profissional" else ROTULOS[p]
                                 for p in conta.perfis)
        iniciais = "".join(parte[0] for parte in conta.nome.split()[:2]).upper() or "S"
        perfil.markdown(f"**◉ {iniciais} · {conta.nome}**")
        perfil.text(nome_perfil)
