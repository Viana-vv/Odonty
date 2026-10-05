"""Páginas da equipe. A identidade é revalidada por app.py antes de renderizar."""
from datetime import date
from pathlib import Path
from time import monotonic

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
                    if area["chave"] != "inicio":
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
