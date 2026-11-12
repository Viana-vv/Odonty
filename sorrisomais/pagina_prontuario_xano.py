"""Tela do Prontuário com suporte ao agregado e compatibilidade legada."""

from datetime import datetime
from zoneinfo import ZoneInfo

import streamlit as st

from . import pagina_nova_evolucao_xano, sessao
from .api import ErroAcesso
from .cache_xano import carregar_cache
from .icones import icone_html

_CHAVE_PENDENTE = "prontuario_paciente_pendente"
_METODOS_AGREGADOS_LISTA = ("listar_prontuarios_agregados", "listar_prontuario_agregado", "listar_prontuarios")
_METODOS_AGREGADOS_ITEM = ("obter_prontuario", "consultar_prontuario", "obter_prontuario_agregado")


def _selecionar_paciente(paciente_id):
    st.session_state[_CHAVE_PENDENTE] = paciente_id


def _carregar_dados(cliente, token, *, force=False):
    """Usa o agregado quando o cliente o expõe; mantém o contrato legado como fallback."""
    for nome in _METODOS_AGREGADOS_LISTA:
        metodo = getattr(cliente, nome, None)
        if callable(metodo):
            agregado = carregar_cache(st.session_state, token, "prontuario-agregado", lambda: metodo(token), force=force)
            return {"agregado": agregado, "consultas": [], "registros": []}
    for nome in _METODOS_AGREGADOS_ITEM:
        metodo = getattr(cliente, nome, None)
        if callable(metodo):
            agregado = carregar_cache(
                st.session_state, token, "prontuario-agregado", lambda: metodo(token, None), force=force
            )
            return {"agregado": agregado, "consultas": [], "registros": []}
    consultas = carregar_cache(st.session_state, token, "consultas", lambda: cliente.listar_consultas(token), force=force)
    registros = carregar_cache(
        st.session_state, token, "registros-clinicos", lambda: cliente.listar_registros_clinicos(token), force=force
    )
    return {"agregado": None, "consultas": consultas, "registros": registros}


def _itens_agregados(agregado):
    if isinstance(agregado, list):
        return [item for item in agregado if isinstance(item, dict)]
    if isinstance(agregado, dict):
        for chave in ("prontuarios", "itens", "pacientes"):
            itens = agregado.get(chave)
            if isinstance(itens, list):
                return [item for item in itens if isinstance(item, dict)]
        return [agregado]
    return []


def _paciente_do_agregado(item):
    paciente = item.get("paciente")
    return paciente if isinstance(paciente, dict) else item


def _id_paciente(item):
    paciente = _paciente_do_agregado(item)
    valor = paciente.get("id", item.get("paciente_id"))
    return valor if isinstance(valor, int) and valor > 0 else None


def _nome_paciente(item):
    paciente = _paciente_do_agregado(item)
    nome = paciente.get("nome") or item.get("paciente_nome")
    return nome.strip() if isinstance(nome, str) and nome.strip() else None


def _pacientes_disponiveis(consultas, registros, agregado=None):
    pacientes = {}
    for item in _itens_agregados(agregado):
        paciente_id = _id_paciente(item)
        if paciente_id is not None:
            pacientes[paciente_id] = _nome_paciente(item) or f"ID {paciente_id}"
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


def _valor_ou_nao_informado(valor):
    if valor is None or (isinstance(valor, str) and not valor.strip()):
        return "Não informado"
    return str(valor)


def _endereco(paciente):
    endereco = paciente.get("endereco")
    if isinstance(endereco, str) and endereco.strip():
        return endereco.strip()
    if not isinstance(endereco, dict):
        endereco = paciente
    partes = []
    for chave in ("logradouro", "numero", "complemento", "bairro", "cidade", "estado", "cep"):
        valor = endereco.get(chave)
        if valor is not None and str(valor).strip():
            partes.append(str(valor).strip())
    return ", ".join(partes) if partes else "Não informado"


def _renderizar_resumo(item):
    paciente = _paciente_do_agregado(item)
    st.subheader("Dados do Paciente")
    colunas = st.columns(5)
    campos = (
        ("Nome", paciente.get("nome")),
        ("CPF", paciente.get("cpf")),
        ("Nascimento", paciente.get("data_nascimento") or paciente.get("nascimento")),
        ("Telefone", paciente.get("telefone") or paciente.get("celular")),
        ("Endereço", _endereco(paciente)),
    )
    for coluna, (rotulo, valor) in zip(colunas, campos):
        with coluna:
            st.caption(rotulo)
            st.write(_valor_ou_nao_informado(valor))


def _renderizar_historico(registros):
    if not registros:
        st.info("Este Paciente ainda não possui Registros Clínicos disponíveis.")
        return
    for registro in registros:
        with st.container(key=f"cartao-registro-clinico-{registro.get('id', 'sem-id')}", border=True):
            paciente = registro.get("paciente_nome")
            profissional = registro.get("profissional_nome")
            st.subheader(paciente if isinstance(paciente, str) and paciente.strip() else "Registro Clínico")
            st.caption(_data_legivel(registro.get("registrado_em")))
            if isinstance(profissional, str) and profissional.strip():
                st.caption(f"Profissional responsável · {profissional}")
            conteudo = registro.get("conteudo")
            if isinstance(conteudo, str) and conteudo.strip():
                st.write(conteudo)
            st.caption(f"Registro #{registro.get('id', '—')}")
            for retificacao in registro.get("retificacoes", []):
                with st.container(key=f"retificacao-registro-{retificacao.get('id', 'sem-id')}", border=True):
                    st.caption(
                        f"Retificação #{retificacao.get('id', '—')} · "
                        f"{_data_legivel(retificacao.get('criada_em'))} · "
                        f"Profissional ID {retificacao.get('profissional_id', '—')}"
                    )
                    if isinstance(retificacao.get("justificativa"), str):
                        st.caption(f"Justificativa: {retificacao['justificativa']}")
                    if isinstance(retificacao.get("conteudo"), str) and retificacao["conteudo"].strip():
                        st.write(retificacao["conteudo"])


_SECOES = (
    ("Anamnese", "anamnese", "Este Paciente ainda não possui Anamnese registrada."),
    ("Histórico Odontológico", "historico_odontologico", "Não há Histórico Odontológico registrado."),
    ("Odontograma", "odontograma", "Odontograma ainda não disponível neste MVP."),
    ("Exame Clínico", "exame_clinico", "Nenhum Exame Clínico registrado."),
    ("Diagnósticos", "diagnosticos", "Nenhum Diagnóstico registrado."),
    ("Plano de Tratamento", "plano_tratamento", "Não há Plano de Tratamento registrado."),
    ("Procedimentos realizados", "procedimentos", "Nenhum Procedimento relacionado encontrado."),
    ("Exames e Imagens", "exames", "Este Paciente não possui Exames disponíveis."),
    ("Prescrições", "prescricoes", "Nenhuma Prescrição registrada."),
    ("Evolução Clínica", "evolucoes", "Este Paciente ainda não possui Registros Clínicos disponíveis."),
    ("Documentos", "documentos", "Nenhum Documento disponível."),
)


def _renderizar_valor_secao(valor, vazio):
    if valor is None or valor == [] or valor == {} or valor == "":
        st.info(vazio)
        return
    if isinstance(valor, list):
        for item in valor:
            if isinstance(item, dict):
                titulo = item.get("titulo") or item.get("tipo") or item.get("nome")
                if titulo:
                    st.markdown(f"**{titulo}**")
                restante = {chave: valor for chave, valor in item.items() if chave not in {"titulo", "tipo", "nome"}}
                if restante:
                    st.json(restante)
            elif isinstance(item, str) and item.strip():
                st.write(item)
        return
    if isinstance(valor, dict):
        st.json(valor)
        return
    st.write(valor)


def renderizar(cliente, conta):
    """Renderiza o Prontuário apenas para perfis clínicos reconhecidos."""
    cabecalho, acao = st.columns([3, 1], vertical_alignment="center")
    cabecalho.title("Prontuários")
    cabecalho.markdown("Consulte o resumo do Paciente e as seções clínicas autorizadas.")
    atualizar = acao.button("Atualizar Prontuário", key="prontuario-atualizar")
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
        with st.spinner("Carregando Prontuário…"):
            dados = _carregar_dados(cliente, credencial.token, force=atualizar)
    except ErroAcesso as error:
        if error.status == 401:
            sessao.limpar(st.session_state)
            st.error("Sua sessão expirou. Entre novamente.")
        else:
            st.error(str(error))
        return
    except Exception:
        st.error("Não foi possível carregar o Prontuário. Tente novamente em instantes.")
        return
    consultas, registros, agregado = dados["consultas"], dados["registros"], dados["agregado"]
    pacientes = _pacientes_disponiveis(consultas, registros, agregado)
    agregado_individual = bool(_itens_agregados(agregado)) and not pacientes
    if not pacientes and not agregado_individual:
        st.info("Não há Pacientes ou Prontuários disponíveis neste escopo.")
        return
    ids = list(pacientes)
    opcoes = [None, *ids]
    pendente = st.session_state.pop(_CHAVE_PENDENTE, None)
    if pendente is not None and pendente in opcoes:
        st.session_state["prontuario_paciente_id"] = pendente
    if st.session_state.get("prontuario_paciente_id") not in opcoes:
        st.session_state["prontuario_paciente_id"] = None
    nomes = {paciente_id: pacientes[paciente_id] for paciente_id in ids}
    if "profissional" in perfis:
        pagina_nova_evolucao_xano.renderizar(cliente, conta, consultas, pacientes=nomes)
        if not st.session_state.get(sessao.CHAVE):
            return
    seletor, aviso_coluna = st.columns([1, 1], vertical_alignment="bottom")
    with seletor:
        selecionado = st.selectbox("Paciente", opcoes, format_func=lambda paciente_id: "Todos" if paciente_id is None else nomes[paciente_id], key="prontuario_paciente_id")
    with aviso_coluna:
        st.markdown(f'{icone_html("shield-check")} Acesso clínico restrito', unsafe_allow_html=True)
    item = _itens_agregados(agregado)[0] if agregado_individual else None
    if selecionado is not None:
        item = next((item for item in _itens_agregados(agregado) if _id_paciente(item) == selecionado), None)
        if item is None and agregado is None:
            item = {"paciente": {"id": selecionado, "nome": nomes[selecionado]}}
        if item is None:
            try:
                for nome in _METODOS_AGREGADOS_ITEM:
                    metodo = getattr(cliente, nome, None)
                    if callable(metodo):
                        item = metodo(credencial.token, selecionado)
                        break
            except ErroAcesso as error:
                if error.status == 401:
                    sessao.limpar(st.session_state)
                    st.error("Sua sessão expirou. Entre novamente.")
                else:
                    st.error(str(error))
                return
    if item is not None:
        _renderizar_resumo(item)
        if selecionado is None and agregado_individual:
            st.markdown("\n".join(f"### {nome}" for nome, _, _ in _SECOES))
    recentes, linha_tempo = st.columns([0.85, 1.8], gap="medium")
    with recentes:
        with st.container(key="lista-pacientes-recentes", border=True):
            st.subheader("Pacientes recentes")
            for paciente_id in ids:
                quantidade = sum(reg.get("paciente_id") == paciente_id for reg in registros)
                st.button(f"{nomes[paciente_id]}  ·  {quantidade} registro(s)", key=f"prontuario-paciente-{paciente_id}", type="primary" if paciente_id == selecionado else "secondary", width="stretch", on_click=_selecionar_paciente, args=(paciente_id,))
    with linha_tempo:
        registros_paciente = [reg for reg in registros if selecionado is None or reg.get("paciente_id") == selecionado]
        if selecionado is None and not agregado_individual:
            _renderizar_historico(registros_paciente)
        else:
            dados_agregado = item if isinstance(item, dict) else None
            for nome, chave, vazio in _SECOES:
                st.write(f"### {nome}")
                if chave == "evolucoes" and agregado is None:
                    _renderizar_historico(registros_paciente)
                else:
                    _renderizar_valor_secao((dados_agregado or {}).get(chave), vazio)
