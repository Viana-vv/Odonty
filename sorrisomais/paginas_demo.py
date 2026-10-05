"""Telas completas do kit usando apenas o repositório fictício da sessão."""

from datetime import date, time
from pathlib import Path

import streamlit as st

from . import demonstracao, navegacao, sessao
from .api import ROTULOS
from .paginas_equipe import renderizar_topbar

STATUS_CONSULTA = ("Agendada", "Confirmada", "Em atendimento", "Realizada", "Cancelada", "Falta")
RAIZ = Path(__file__).resolve().parents[1]


def _pagina(chave):
    st.session_state["pagina_equipe"] = chave


def _navegar(chave):
    st.session_state["demo_pagina"] = chave
    st.session_state.pop("demo_mensagem", None)


def _aviso_operacao():
    aviso = st.session_state.pop("demo_mensagem", None)
    if aviso:
        tipo, mensagem = aviso
        getattr(st, tipo)(mensagem)


def _cabecalho(titulo, descricao):
    st.caption("SORRISO+  /  EQUIPE DA CLÍNICA")
    st.title(titulo)
    st.write(descricao)


def _cartao_metrica(coluna, rotulo, valor, descricao, icone):
    with coluna:
        with st.container(key=f"demo-metrica-{rotulo.casefold().replace(' ', '-')}", border=True):
            st.markdown(f"<div class='metrica-icone'>{icone}</div>", unsafe_allow_html=True)
            st.caption(rotulo)
            st.subheader(str(valor))
            st.caption(descricao)


def _pessoa_por_id(itens, identificador):
    return next((item for item in itens if item["id"] == identificador), None)


def _consulta_detalhe(repo, consulta):
    paciente = _pessoa_por_id(repo.dados["pacientes"], consulta["paciente_id"])
    profissional = _pessoa_por_id(repo.dados["profissionais"], consulta["profissional_id"])
    procedimento = _pessoa_por_id(repo.dados["procedimentos"], consulta["procedimento_id"])
    return paciente, profissional, procedimento


def _cartao_consulta(repo, consulta, mostrar_status=True):
    paciente, profissional, procedimento = _consulta_detalhe(repo, consulta)
    horario = f"{consulta['hora']}  ·  {paciente['nome']}" if paciente else consulta["hora"]
    with st.container(key=f"demo-consulta-{consulta['id']}", border=True):
        col_hora, col_dados, col_status = st.columns([0.18, 0.58, 0.24], vertical_alignment="center")
        col_hora.markdown(f"**{horario}**")
        if paciente and profissional and procedimento:
            col_dados.write(f"{procedimento['nome']} · Dr(a). {profissional['nome']}")
        if mostrar_status:
            col_status.markdown(f"<span class='status status-{consulta['situacao'].casefold().replace(' ', '-')}'>{consulta['situacao']}</span>", unsafe_allow_html=True)


def _nova_consulta(repo, perfis, dia_padrao):
    st.subheader("Nova consulta")
    pacientes = repo.listar("pacientes")
    profissionais = [p for p in repo.listar("profissionais") if p["situacao"] == "ativo"]
    procedimentos = [p for p in repo.listar("procedimentos") if p["situacao"] == "ativo"]
    if not pacientes or not profissionais or not procedimentos:
        st.info("Cadastre Pacientes, Profissionais e Procedimentos antes de agendar.")
        return
    p_opcoes = {p["id"]: p["nome"] for p in pacientes}
    prof_opcoes = {p["id"]: f"{p['nome']} · {p['especialidade']}" for p in profissionais}
    proc_opcoes = {p["id"]: f"{p['nome']} · {p['duracao_minutos']} min" for p in procedimentos}
    with st.form("demo-form-consulta", border=True):
        paciente_id = st.selectbox("Paciente *", list(p_opcoes), format_func=p_opcoes.get)
        col_data, col_hora = st.columns(2)
        dia = col_data.date_input("Data *", value=dia_padrao, min_value=date.today(), format="DD/MM/YYYY")
        horario = col_hora.time_input("Horário *", value=time(9, 0), step=900)
        profissional_id = st.selectbox("Profissional *", list(prof_opcoes), format_func=prof_opcoes.get)
        procedimento_id = st.selectbox("Procedimento *", list(proc_opcoes), format_func=proc_opcoes.get)
        observacoes = st.text_area("Observações administrativas", max_chars=500)
        enviada = st.form_submit_button("Agendar consulta", type="primary", width="stretch")
    if enviada:
        try:
            repo.agendar_consulta(paciente_id, profissional_id, procedimento_id,
                                  dia.isoformat(), horario.strftime("%H:%M"), observacoes)
            st.session_state["demo_mensagem"] = ("success", "Consulta criada na demonstração da sessão.")
            st.rerun()
        except ValueError as error:
            st.error(str(error))


def _pagina_inicio(repo, conta, perfis):
    hoje = date.today()
    metricas = repo.metricas(hoje)
    consultas = sorted((c for c in repo.listar("consultas") if c["data"] == hoje.isoformat()),
                       key=lambda c: c["hora"])
    ativas = [c for c in consultas if c["situacao"] not in {"Realizada", "Cancelada", "Falta"}]
    proxima = ativas[0] if ativas else None
    _cabecalho("Visão geral", "Aqui está um resumo da clínica hoje.")
    st.caption(hoje.strftime("%A, %d de %B de %Y").upper())
    cols = st.columns(4)
    _cartao_metrica(cols[0], "Consultas hoje", metricas["consultas"],
                    f"{metricas['aguardando']} ainda aguardando", "▣")
    _cartao_metrica(cols[1], "Atendimentos", metricas["realizadas"], "concluídos hoje", "✓")
    _cartao_metrica(cols[2], "Pacientes ativos", metricas["pacientes"], "cadastros na demonstração", "♙")
    _cartao_metrica(cols[3], "Próxima consulta", proxima["hora"] if proxima else "—",
                    _consulta_detalhe(repo, proxima)[0]["nome"] if proxima else "nenhuma marcada", "◷")
    esquerda, direita = st.columns([1.65, 1], gap="medium")
    with esquerda:
        with st.container(key="demo-painel-agenda", border=True):
            st.subheader("Agenda de hoje")
            st.caption(f"{len(consultas)} consultas")
            if not consultas:
                st.info("Nenhuma consulta para hoje.")
            for consulta in consultas[:5]:
                _cartao_consulta(repo, consulta)
            st.button("Ver agenda completa →", on_click=_navegar, args=("agenda",), key="demo-inicio-agenda")
    with direita:
        with st.container(key="demo-painel-atalhos", border=True):
            st.subheader("Acesso rápido")
            if perfis.intersection({"administrador", "recepcionista"}):
                st.button("Novo paciente  ›", on_click=_navegar, args=("pacientes",), key="demo-inicio-paciente", width="stretch")
            if "profissional" in perfis:
                st.button("Abrir prontuário  ›", on_click=_navegar, args=("prontuarios",), key="demo-inicio-prontuario", width="stretch")
            st.button("Visualizar agenda  ›", on_click=_navegar, args=("agenda",), key="demo-inicio-agenda-atalho", width="stretch")
        total = metricas["consultas"]
        taxa = metricas["confirmadas"] / total if total else 0
        with st.container(key="demo-painel-confirmadas", border=True):
            st.markdown(f"**{metricas['confirmadas']} confirmadas**")
            st.caption("para o restante do dia")
            st.progress(taxa)


def _pagina_agenda(repo, perfis):
    _cabecalho("Agenda", "Consulte e organize os horários da equipe.")
    hoje = date.today()
    col_data, col_status, col_busca, col_novo = st.columns([1.2, 1, 1.6, 1])
    dia = col_data.date_input("Data", value=hoje, format="DD/MM/YYYY", key="demo-agenda-data")
    status = col_status.selectbox("Situação", ["Todas", *STATUS_CONSULTA], key="demo-agenda-status")
    busca = col_busca.text_input("Buscar paciente", key="demo-agenda-busca")
    pode_agendar = bool(perfis.intersection({"administrador", "recepcionista"}))
    if pode_agendar:
        col_novo.button("+ Nova consulta", on_click=lambda: _navegar("nova_consulta"), type="primary", key="demo-agenda-nova")
    consultas = [c for c in repo.listar("consultas") if c["data"] == dia.isoformat()]
    if status != "Todas":
        consultas = [c for c in consultas if c["situacao"] == status]
    termo = busca.strip().casefold()
    if termo:
        consultas = [c for c in consultas
                     if termo in (_pessoa_por_id(repo.dados["pacientes"], c["paciente_id"]) or {}).get("nome", "").casefold()]
    st.caption(f"{len(consultas)} consultas encontradas")
    if not consultas:
        st.info("Nenhuma consulta encontrada para os filtros selecionados.")
    for consulta in sorted(consultas, key=lambda c: c["hora"]):
        paciente, profissional, procedimento = _consulta_detalhe(repo, consulta)
        with st.container(key=f"demo-agenda-linha-{consulta['id']}", border=True):
            a, b, c = st.columns([1, 3, 1.2], vertical_alignment="center")
            a.markdown(f"### {consulta['hora']}")
            b.markdown(f"**{paciente['nome']}**  ·  {procedimento['nome']}\n\nDr(a). {profissional['nome']}")
            novo_status = c.selectbox("Situação", STATUS_CONSULTA, index=STATUS_CONSULTA.index(consulta["situacao"]), key=f"demo-status-{consulta['id']}", label_visibility="collapsed")
            if novo_status != consulta["situacao"] and c.button("Salvar", key=f"demo-status-salvar-{consulta['id']}"):
                repo.alterar_situacao_consulta(consulta["id"], novo_status)
                st.rerun()
    if st.session_state.get("demo_pagina") == "nova_consulta":
        st.divider()
        _nova_consulta(repo, perfis, dia)


def _form_paciente(repo, paciente=None):
    titulo = "Editar paciente" if paciente else "Novo paciente"
    st.subheader(titulo)
    with st.form("demo-form-paciente", border=True):
        nome = st.text_input("Nome completo *", value=(paciente or {}).get("nome", ""), max_chars=120)
        cpf = st.text_input("CPF fictício *", value=(paciente or {}).get("cpf", ""), max_chars=14)
        col_nasc, col_tel = st.columns(2)
        nascimento = col_nasc.date_input(
            "Data de nascimento *", value=date.fromisoformat(paciente["nascimento"]) if paciente else None,
            min_value=date(1900, 1, 1), max_value=date.today(), format="DD/MM/YYYY",
        )
        telefone = col_tel.text_input("Telefone *", value=(paciente or {}).get("telefone", ""))
        col_email, col_celular = st.columns(2)
        email = col_email.text_input("E-mail *", value=(paciente or {}).get("email", ""))
        celular = col_celular.text_input("Celular", value=(paciente or {}).get("celular", ""))
        observacoes = st.text_area("Observações administrativas", value=(paciente or {}).get("observacoes", ""))
        salvar = st.form_submit_button("Salvar alterações" if paciente else "Cadastrar paciente", type="primary")
    if salvar:
        try:
            repo.salvar_paciente({
                "nome": nome, "cpf": cpf, "nascimento": nascimento.isoformat(),
                "telefone": telefone, "email": email, "celular": celular, "observacoes": observacoes,
            }, paciente["id"] if paciente else None)
            st.session_state["demo_mensagem"] = ("success", "Cadastro salvo somente nesta demonstração.")
            st.session_state["demo_pagina"] = "pacientes"
            st.rerun()
        except ValueError as error:
            st.error(str(error))


def _pagina_pacientes(repo, perfis):
    _cabecalho("Pacientes", "Localize cadastros e mantenha as informações administrativas organizadas.")
    busca, novo = st.columns([3, 1])
    termo = busca.text_input("Buscar por nome, CPF ou telefone", key="demo-busca-pacientes")
    if perfis.intersection({"administrador", "recepcionista"}):
        novo.button("+ Novo paciente", type="primary", key="demo-novo-paciente", on_click=_navegar, args=("novo_paciente",))
    pacientes = repo.buscar_pacientes(termo)
    st.caption(f"{len(pacientes)} pacientes")
    if not pacientes:
        st.info("Nenhum paciente encontrado. Ajuste sua busca ou cadastre um paciente.")
    for paciente in pacientes:
        with st.container(key=f"demo-cartao-paciente-{paciente['id']}", border=True):
            col_dados, col_acoes = st.columns([3, 1])
            col_dados.subheader(paciente["nome"])
            col_dados.caption(f"CPF {paciente['cpf']} · Nascimento {paciente['nascimento']} · {paciente['telefone']}")
            col_dados.write(paciente["email"])
            if perfis.intersection({"administrador", "recepcionista"}):
                col_acoes.button("Editar", key=f"demo-editar-paciente-{paciente['id']}",
                                 on_click=_navegar, args=(f"editar_paciente:{paciente['id']}",))
            if "profissional" in perfis:
                col_acoes.button("Prontuário", key=f"demo-paciente-prontuario-{paciente['id']}",
                                 on_click=_navegar, args=(f"prontuarios:{paciente['id']}",))
    pagina = st.session_state.get("demo_pagina", "pacientes")
    if pagina == "novo_paciente":
        st.divider()
        _form_paciente(repo)
    elif pagina.startswith("editar_paciente:"):
        paciente_id = int(pagina.split(":", 1)[1])
        _form_paciente(repo, _pessoa_por_id(repo.dados["pacientes"], paciente_id))


def _pagina_profissionais(repo, perfis):
    _cabecalho("Profissionais", "Consulte a equipe e confira sua situação cadastral.")
    pode_administrar = "administrador" in perfis
    if pode_administrar and st.button("+ Novo profissional", type="primary", key="demo-novo-profissional"):
        _navegar("novo_profissional")
    pagina = st.session_state.get("demo_pagina", "profissionais")
    if pagina == "novo_profissional" and pode_administrar:
        with st.form("demo-form-profissional", border=True):
            nome = st.text_input("Nome completo *")
            especialidade = st.text_input("Especialidade *")
            cro = st.text_input("CRO *", placeholder="SP-000000")
            telefone = st.text_input("Telefone")
            email = st.text_input("E-mail")
            enviado = st.form_submit_button("Cadastrar profissional", type="primary")
        if enviado:
            try:
                repo.salvar_profissional({"nome": nome, "especialidade": especialidade,
                                         "cro": cro, "telefone": telefone, "email": email})
                st.session_state["demo_mensagem"] = ("success", "Profissional incluído somente nesta demonstração.")
                _navegar("profissionais")
                st.rerun()
            except ValueError as error:
                st.error(str(error))
    profissionais = repo.listar("profissionais")
    cols = st.columns(2)
    for indice, profissional in enumerate(profissionais):
        with cols[indice % 2]:
            with st.container(key=f"demo-cartao-profissional-{profissional['id']}", border=True):
                st.subheader(profissional["nome"])
                st.caption(f"{profissional['especialidade']} · CRO {profissional['cro']}")
                st.write(f"{profissional['telefone']} · {profissional['email']}")
                st.markdown(f"Situação: **{profissional['situacao'].title()}**")
                if pode_administrar:
                    ativo = profissional["situacao"] == "ativo"
                    if st.button("Inativar" if ativo else "Reativar", key=f"demo-prof-status-{profissional['id']}"):
                        repo.alterar_situacao_profissional(profissional["id"], not ativo)
                        st.rerun()


def _pagina_prontuarios(repo, perfis):
    _cabecalho("Prontuários", "Histórico clínico do Paciente selecionado.")
    try:
        registros = repo.listar_registros_clinicos(perfis)
    except PermissionError:
        st.error("Acesso restrito a Profissionais autorizados.")
        return
    pacientes = repo.listar("pacientes")
    opcoes = {None: "Todos os pacientes", **{p["id"]: p["nome"] for p in pacientes}}
    selecionado = st.selectbox("Filtrar por paciente", list(opcoes), format_func=opcoes.get)
    if selecionado is not None:
        registros = [r for r in registros if r["paciente_id"] == selecionado]
    nova = st.button("+ Nova evolução", type="primary", key="demo-nova-evolucao")
    if nova:
        st.session_state["demo_pagina"] = f"nova_evolucao:{selecionado or ''}"
    pagina = st.session_state.get("demo_pagina", "prontuarios")
    if pagina.startswith("nova_evolucao:"):
        paciente_default = pagina.split(":", 1)[1]
        paciente_ids = list(opcoes.keys())[1:]
        default_index = paciente_ids.index(int(paciente_default)) if paciente_default and int(paciente_default) in paciente_ids else 0
        profissionais = repo.listar("profissionais")
        pro_opcoes = {p["id"]: p["nome"] for p in profissionais}
        with st.form("demo-form-evolucao", border=True):
            paciente_id = st.selectbox("Paciente *", paciente_ids, index=default_index,
                                       format_func=opcoes.get, key="demo-evolucao-paciente")
            profissional_id = st.selectbox("Profissional *", list(pro_opcoes), format_func=pro_opcoes.get)
            data_atendimento = st.date_input("Data do atendimento *", value=date.today(), max_value=date.today(), format="DD/MM/YYYY")
            procedimento = st.text_input("Procedimento *")
            evolucao = st.text_area("Evolução e observações *")
            enviar = st.form_submit_button("Salvar evolução", type="primary")
        if enviar:
            try:
                repo.registrar_evolucao(perfis, paciente_id, profissional_id,
                                        data_atendimento.isoformat(), procedimento, evolucao)
                st.session_state["demo_mensagem"] = ("success", "Evolução fictícia salva nesta sessão.")
                _navegar("prontuarios")
                st.rerun()
            except (ValueError, PermissionError) as error:
                st.error(str(error))
    if not registros:
        st.info("Sem evoluções registradas. Use Nova evolução para criar o primeiro registro demonstrativo.")
    for registro in registros:
        paciente = _pessoa_por_id(pacientes, registro["paciente_id"])
        profissional = _pessoa_por_id(repo.dados["profissionais"], registro["profissional_id"])
        with st.container(key=f"demo-cartao-evolucao-{registro['id']}", border=True):
            st.caption(f"{registro['data']}  ·  {paciente['nome']}  ·  Dr(a). {profissional['nome']}")
            st.subheader(registro["procedimento"])
            st.write(registro["evolucao"])


def _pagina_procedimentos(repo):
    _cabecalho("Procedimentos", "Catálogo demonstrativo de serviços e valores de referência.")
    procedimentos = repo.listar("procedimentos")
    cols = st.columns(3)
    for indice, procedimento in enumerate(procedimentos):
        with cols[indice % len(cols)]:
            with st.container(key=f"demo-cartao-procedimento-{procedimento['id']}", border=True):
                st.subheader(procedimento["nome"])
                st.caption(f"Duração estimada · {procedimento['duracao_minutos']} minutos")
                st.markdown(f"### R$ {procedimento['valor_referencia']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
                st.caption("Valor de referência fictício; sem cobrança.")


def renderizar(conta, cliente):
    """Renderiza as áreas permitidas com dados de demonstração da sessão."""
    perfis = set(conta.perfis)
    pode_paciente = (cliente.configuracao.cadastro_paciente_habilitado
                     and bool(perfis.intersection({"administrador", "recepcionista"})))
    repo = demonstracao.RepositorioDemonstracao(st.session_state)
    areas = navegacao.areas_visiveis(perfis, modo_demonstracao=True,
                                     cadastro_paciente_habilitado=pode_paciente)
    atual = st.session_state.get("demo_pagina", "inicio")
    if not navegacao.pode_acessar(perfis, atual.split(":", 1)[0]):
        atual = "inicio"
        st.session_state["demo_pagina"] = atual
    ocupada = bool(st.session_state.get("cad_processando") or st.session_state.get("pac_processando"))
    with st.container(key="layout-equipe"):
        renderizar_topbar(conta, atual.split(":", 1)[0])
        menu, conteudo = st.columns([0.205, 0.795], gap="medium", vertical_alignment="top")
        with menu:
            with st.container(key="menu-equipe", border=True):
                st.markdown("### Sorriso+")
                st.caption("EQUIPE DA CLÍNICA")
                for area in areas:
                    selecionada = area["chave"] == atual.split(":", 1)[0]
                    st.button(area["rotulo"], key=f"demo-nav-{area['chave']}",
                              type="primary" if selecionada else "secondary",
                              on_click=_navegar, args=(area["chave"],),
                              disabled=ocupada, width="stretch")
                st.divider()
                st.caption("SEU ACESSO")
                st.write(conta.nome)
                st.caption(" · ".join("Dentista" if p == "profissional" else ROTULOS[p] for p in conta.perfis))
                if st.button("Sair", key="sair", width="stretch", disabled=ocupada):
                    with st.spinner("Encerrando seu acesso…"):
                        mensagem = sessao.sair(st.session_state, cliente)
                    st.session_state["aviso"] = ("info", mensagem)
                    st.rerun()
        with conteudo:
            with st.container(key="conteudo-equipe", border=True):
                st.info("Modo de demonstração: dados fictícios guardados somente nesta sessão; não são enviados ao Xano.", icon="ℹ️")
                _aviso_operacao()
                chave = atual.split(":", 1)[0]
                if chave == "inicio":
                    _pagina_inicio(repo, conta, perfis)
                elif chave == "agenda":
                    _pagina_agenda(repo, perfis)
                elif chave == "pacientes":
                    _pagina_pacientes(repo, perfis)
                elif chave == "profissionais":
                    _pagina_profissionais(repo, perfis)
                elif chave == "prontuarios":
                    _pagina_prontuarios(repo, perfis)
                elif chave == "procedimentos":
                    _pagina_procedimentos(repo)
