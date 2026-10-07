"""Páginas da equipe. A identidade é revalidada por app.py antes de renderizar."""
from datetime import date, datetime, time, timedelta
from pathlib import Path
from time import monotonic
from zoneinfo import ZoneInfo

import streamlit as st

from .api import ErroAcesso, ROTULOS
from . import sessao, pagina_paciente, navegacao

ESPECIALIDADES_CACHE_TTL_SEGUNDOS = 300
ESPECIALIDADES_RETRY_SEGUNDOS = 20
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


def _data_api(dia, final=False):
    limite = datetime.combine(dia + (timedelta(days=1) if final else timedelta()), time.min,
                              tzinfo=ZoneInfo("America/Sao_Paulo"))
    return limite.isoformat(timespec="seconds")


def _renderizar_agenda(cliente, conta):
    st.title("Agenda")
    aviso_agenda = st.session_state.pop("agenda_aviso", None)
    if aviso_agenda:
        getattr(st, aviso_agenda[0])(aviso_agenda[1])
    perfis = set(conta.perfis)
    token = st.session_state[sessao.CHAVE].token
    data_col, status_col, busca_col = st.columns([1, 1, 1.4], gap="small")
    dia = data_col.date_input("Data", value=st.session_state.get("agenda_data", date.today()),
                              format="DD/MM/YYYY", key="agenda_data_input")
    situacao = status_col.selectbox("Situação", ["Todas", "Agendada", "Confirmada",
        "Em atendimento", "Realizada", "Cancelada", "Falta"], key="agenda_situacao")
    busca = busca_col.text_input("Buscar Paciente ou Procedimento", key="agenda_busca").strip().casefold()
    anterior, hoje, proximo, novo = st.columns([1, 1, 1, 1.5], vertical_alignment="center")
    anterior.button("‹ Dia anterior", key="agenda-anterior", width="stretch",
                    on_click=_navegar_data_agenda, args=(-1,))
    hoje.button("Hoje", key="agenda-hoje", width="stretch",
                on_click=_ir_para_hoje_na_agenda)
    proximo.button("Próximo dia ›", key="agenda-proximo", width="stretch",
                   on_click=_navegar_data_agenda, args=(1,))
    pode_agendar = bool(perfis.intersection({"administrador", "recepcionista"}))
    if pode_agendar:
        novo.button("＋ Nova consulta", key="agenda-nova", type="primary", width="stretch",
                    on_click=lambda: st.session_state.update(agenda_nova=not st.session_state.get("agenda_nova", False)))

    try:
        consultas = cliente.listar_consultas(token, inicio=_data_api(dia), fim=_data_api(dia, True))
    except ErroAcesso as error:
        if error.status in (401, 403):
            sessao.limpar(st.session_state)
            st.error(str(error))
            return
        st.error("Não foi possível carregar a Agenda. Tente novamente.")
        if st.button("Tentar novamente", key="agenda-retry"):
            st.rerun()
        return

    if situacao != "Todas":
        consultas = [c for c in consultas if c["situacao"] == situacao]
    if busca:
        consultas = [c for c in consultas if busca in c["paciente_nome"].casefold()
                     or any(busca in p.casefold() for p in c["procedimentos"])]
    consultas.sort(key=lambda c: (c["inicio_em"], c["id"]))
    st.caption(f"{len(consultas)} consulta(s) · {dia.strftime('%d/%m/%Y')}")

    if st.session_state.get("agenda_nova") and pode_agendar:
        _renderizar_formulario_agenda(cliente, token, dia)
    if not consultas:
        st.info("Nenhuma consulta encontrada para esta data e filtros.")
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
                motivo = motivo_col.text_input("Motivo do cancelamento", max_chars=1000,
                    key=f"agenda-motivo-{consulta['id']}", disabled=proxima != "Cancelada")
                confirmar = motivo_col.checkbox("Confirmo o cancelamento", key=f"agenda-confirmar-{consulta['id']}",
                    disabled=proxima != "Cancelada")
                enviar = enviar_col.button("Atualizar", key=f"agenda-atualizar-{consulta['id']}", width="stretch")
                if enviar:
                    if proxima == "Cancelada" and not motivo.strip():
                        st.error("Informe o motivo do cancelamento.")
                    elif proxima == "Cancelada" and not confirmar:
                        st.error("Confirme o cancelamento antes de continuar.")
                    else:
                        try:
                            cliente.atualizar_situacao_consulta(token, consulta["id"], proxima,
                                motivo_cancelamento=motivo.strip() if proxima == "Cancelada" else None)
                            st.session_state["agenda_aviso"] = ("success", "Situação da consulta atualizada.")
                            st.rerun()
                        except ErroAcesso as error:
                            st.error(str(error))


def _renderizar_formulario_agenda(cliente, token, dia):
    try:
        opcoes = cliente.listar_opcoes_agenda(token)
    except ErroAcesso as error:
        st.error(str(error) if error.status in (401, 403) else "Não foi possível carregar as opções de agendamento.")
        return
    if not opcoes["pacientes"] or not opcoes["profissionais"]:
        st.info("Cadastre Pacientes e Profissionais ativos antes de agendar.")
        return
    with st.form("agenda-form-nova-consulta", border=True):
        st.subheader("Nova consulta")
        pacientes = {i["id"]: i["nome"] for i in opcoes["pacientes"]}
        profissionais = {i["id"]: i["nome"] for i in opcoes["profissionais"]}
        procedimentos = {i["id"]: i["nome"] for i in opcoes["procedimentos"]}
        paciente_id = st.selectbox("Paciente", list(pacientes), format_func=pacientes.get, key="agenda-paciente")
        profissional_id = st.selectbox("Profissional", list(profissionais), format_func=profissionais.get, key="agenda-profissional")
        inicio, fim = _data_api(dia), _data_api(dia, True)
        try:
            disponibilidades = cliente.listar_disponibilidades(token, profissional_id, inicio, fim)
        except ErroAcesso as error:
            st.error("Não foi possível carregar os horários disponíveis." if error.status not in (401, 403) else str(error))
            disponibilidades = []
        horarios = {d["id"]: f"{datetime.fromisoformat(d['inicio'].replace('Z', '+00:00')).astimezone(ZoneInfo('America/Sao_Paulo')):%H:%M} – {datetime.fromisoformat(d['fim'].replace('Z', '+00:00')).astimezone(ZoneInfo('America/Sao_Paulo')):%H:%M}" for d in disponibilidades}
        if not horarios:
            st.info("Nenhum horário disponível para este profissional nesta data.")
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
            st.session_state["agenda_nova"] = False
            st.session_state["agenda_aviso"] = ("success", "Consulta agendada.")
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
    st.caption("Cadastre um dentista e associe uma especialidade ativa.")
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
        email, senha = st.columns(2, gap="medium")
        email.text_input("E-mail do profissional", key="cad_email", max_chars=254,
                         placeholder="profissional@clinica.com", disabled=ocupado)
        senha.text_input("Senha inicial", key="cad_senha", type="password", max_chars=128,
                         help="De 12 a 128 caracteres.", disabled=ocupado)
        st.text_input("Confirmar senha", key="cad_confirmacao", type="password",
                      max_chars=128, disabled=ocupado)
        cancelar, enviar = st.columns([1, 1.3], gap="small", vertical_alignment="center")
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
        if fechar.button("×", key="cad-fechar-modal", help="Fechar cadastro"):
            voltar()
            st.rerun()
        st.divider()
        renderizar_cadastro(cliente)


def renderizar_inicio(conta, administrador, pode_cadastrar_paciente):
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
    acao.button("＋ Nova consulta", key="inicio-nova-consulta", disabled=True,
                width="stretch", help="A integração de Consultas com o Xano ainda não está disponível.")

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
            st.button("▤  Abrir prontuário", key="inicio-prontuario-indisponivel",
                      disabled=True, width="stretch",
                      help="A listagem de Prontuários ainda não está integrada ao Xano.")
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

    administrador = "administrador" in conta.perfis
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
    pagina = st.session_state.get("pagina_equipe", "inicio")
    ocupado = (st.session_state.get("cad_processando", False)
               or st.session_state.get("pac_processando", False))
    with st.container(key="layout-equipe"):
        menu, conteudo = st.columns([0.205, 0.795], gap="medium", vertical_alignment="top")
        with menu:
            with st.container(key="menu-equipe", border=True):
                renderizar_marca_menu()
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
                        st.button(area["rotulo"], key=f"menu-indisponivel-{area['chave']}",
                                  disabled=True, width="stretch",
                                  help="A integração desta área com o Xano ainda não está disponível.")
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
                else:
                    renderizar_topbar(conta, "inicio")
                    renderizar_inicio(conta, administrador, pode_cadastrar_paciente)
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
