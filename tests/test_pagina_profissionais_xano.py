"""Testes da listagem conectada de Profissionais, sem chamadas de rede."""

from contextlib import nullcontext
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from sorrisomais.api import ContaAcesso, Credencial, ErroAcesso
from sorrisomais import pagina_profissionais_xano as pagina


PROFISSIONAIS = [
    {"id": 201, "nome": "Dra. Exemplo Sorriso"},
    {"id": 202, "nome": "Dr. Nome Fictício"},
]


class InterfaceFalsa:
    def __init__(self):
        self.session_state = {"credencial": Credencial(
            "token-ficticio", datetime.now(timezone.utc) + timedelta(hours=1))}
        self.textos = []
        self.infos = []
        self.erros = []
        self.colunas_criadas = []
        self.atualizacoes = []
        self.cliques_atualizar = []

    def button(self, texto, **_kwargs):
        self.atualizacoes.append(texto)
        return self.cliques_atualizar.pop(0) if self.cliques_atualizar else False

    def title(self, texto):
        self.textos.append(texto)

    def write(self, texto):
        self.textos.append(texto)

    def info(self, texto):
        self.infos.append(texto)

    def error(self, texto):
        self.erros.append(texto)

    def spinner(self, _texto):
        return nullcontext()

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def columns(self, quantidade, **_kwargs):
        self.colunas_criadas.append(quantidade)
        return [self] * (quantidade if isinstance(quantidade, int) else len(quantidade))

    def container(self, **_kwargs):
        return nullcontext()

    def markdown(self, texto, **_kwargs):
        self.textos.append(texto)

    def subheader(self, texto):
        self.textos.append(texto)

    def caption(self, texto):
        self.textos.append(texto)


@pytest.fixture
def tela(monkeypatch):
    interface = InterfaceFalsa()
    monkeypatch.setattr(pagina, "st", interface)
    cliente = Mock()
    cliente.listar_opcoes_agenda.return_value = {
        "pacientes": [], "profissionais": PROFISSIONAIS, "procedimentos": [],
    }
    expira = datetime.now(timezone.utc) + timedelta(hours=1)
    conta = ContaAcesso(1, "Conta Fictícia", ("administrador",), expira)
    return interface, cliente, conta


def test_lista_exibe_nome_e_indicador_ativo(tela):
    interface, cliente, conta = tela
    pagina.renderizar(cliente, conta)
    assert "Dra. Exemplo Sorriso" in interface.textos
    assert "Dr. Nome Fictício" in interface.textos
    assert interface.textos.count("Ativo") == 2
    assert "2 profissional(is) ativo(s)" in interface.textos
    assert interface.colunas_criadas == [3, [1, 1], [1, 1]]
    cliente.listar_opcoes_agenda.assert_called_once_with("token-ficticio")


def test_recepcionista_pode_carregar_lista(tela):
    _, cliente, conta = tela
    conta = SimpleNamespace(perfis=("recepcionista",))
    pagina.renderizar(cliente, conta)
    cliente.listar_opcoes_agenda.assert_called_once_with("token-ficticio")


def test_lista_vazia_informa_ausencia_de_profissionais(tela):
    interface, cliente, conta = tela
    cliente.listar_opcoes_agenda.return_value["profissionais"] = []
    pagina.renderizar(cliente, conta)
    assert interface.infos == ["Não há Profissionais ativos para exibir."]


def test_falha_de_api_nao_exibe_resultados(tela):
    interface, cliente, conta = tela
    cliente.listar_opcoes_agenda.side_effect = ErroAcesso("Serviço indisponível.", 503)
    pagina.renderizar(cliente, conta)
    assert interface.erros == ["Serviço indisponível."]
    assert "Dra. Exemplo Sorriso" not in interface.textos


def test_sessao_expirada_limpa_credencial(tela):
    interface, cliente, conta = tela
    cliente.listar_opcoes_agenda.side_effect = ErroAcesso(
        "Sua sessão expirou ou não é válida. Entre novamente.", 401)
    pagina.renderizar(cliente, conta)
    assert interface.erros == ["Sua sessão expirou ou não é válida. Entre novamente."]
    assert "credencial" not in interface.session_state


def test_acesso_negado_preserva_sessao(tela):
    interface, cliente, conta = tela
    credencial = interface.session_state["credencial"]
    cliente.listar_opcoes_agenda.side_effect = ErroAcesso(
        "Sua conta não tem permissão para acessar esta área.", 403)
    pagina.renderizar(cliente, conta)
    assert interface.erros == ["Sua conta não tem permissão para acessar esta área."]
    assert interface.session_state["credencial"] == credencial


def test_perfil_profissional_nao_carrega_dados(tela):
    interface, cliente, _ = tela
    conta = SimpleNamespace(perfis=("profissional",))
    pagina.renderizar(cliente, conta)
    assert interface.infos == ["Seu perfil não tem permissão para consultar esta lista."]
    cliente.listar_opcoes_agenda.assert_not_called()


def test_rerun_reutiliza_cache_da_sessao_por_20_segundos(tela, monkeypatch):
    interface, cliente, conta = tela
    monkeypatch.setattr(pagina.time, "monotonic", lambda: 100.0)

    pagina.renderizar(cliente, conta)
    pagina.renderizar(cliente, conta)

    cliente.listar_opcoes_agenda.assert_called_once_with("token-ficticio")
    assert "Atualizar lista" in interface.atualizacoes


def test_cache_expira_apos_20_segundos(tela, monkeypatch):
    _, cliente, conta = tela
    agora = [100.0]
    monkeypatch.setattr(pagina.time, "monotonic", lambda: agora[0])

    pagina.renderizar(cliente, conta)
    agora[0] = 120.0
    pagina.renderizar(cliente, conta)

    assert cliente.listar_opcoes_agenda.call_count == 2


def test_botao_atualizar_forca_nova_consulta(tela, monkeypatch):
    interface, cliente, conta = tela
    interface.cliques_atualizar = [False, True]
    monkeypatch.setattr(pagina.time, "monotonic", lambda: 100.0)

    pagina.renderizar(cliente, conta)
    pagina.renderizar(cliente, conta)

    assert cliente.listar_opcoes_agenda.call_count == 2


def test_falha_ao_atualizar_nao_mantem_cache_antigo(tela, monkeypatch):
    interface, cliente, conta = tela
    interface.cliques_atualizar = [False, True, False]
    cliente.listar_opcoes_agenda.side_effect = [
        {"pacientes": [], "profissionais": PROFISSIONAIS, "procedimentos": []},
        ErroAcesso("Falha teste.", 503),
        {"pacientes": [], "profissionais": [], "procedimentos": []},
    ]
    monkeypatch.setattr(pagina.time, "monotonic", lambda: 100.0)

    pagina.renderizar(cliente, conta)
    interface.textos.clear()
    pagina.renderizar(cliente, conta)
    assert pagina._CHAVE_CACHE_PROFISSIONAIS not in interface.session_state
    assert "Dra. Exemplo Sorriso" not in interface.textos
    pagina.renderizar(cliente, conta)

    assert cliente.listar_opcoes_agenda.call_count == 3
    assert len(interface.infos) == 1


def test_alteracao_do_token_invalida_cache(tela, monkeypatch):
    interface, cliente, conta = tela
    monkeypatch.setattr(pagina.time, "monotonic", lambda: 100.0)

    pagina.renderizar(cliente, conta)
    interface.session_state["credencial"] = Credencial(
        "outro-token-ficticio", datetime.now(timezone.utc) + timedelta(hours=1))
    pagina.renderizar(cliente, conta)

    assert cliente.listar_opcoes_agenda.call_args_list == [
        (("token-ficticio",),), (("outro-token-ficticio",),),
    ]


def test_401_limpa_cache_e_credencial(tela, monkeypatch):
    interface, cliente, conta = tela
    interface.cliques_atualizar = [False, True]
    cliente.listar_opcoes_agenda.side_effect = [
        {"pacientes": [], "profissionais": PROFISSIONAIS, "procedimentos": []},
        ErroAcesso("Sessao expirada.", 401),
    ]
    monkeypatch.setattr(pagina.time, "monotonic", lambda: 100.0)

    pagina.renderizar(cliente, conta)
    pagina.renderizar(cliente, conta)

    assert pagina._CHAVE_CACHE_PROFISSIONAIS not in interface.session_state
    assert "credencial" not in interface.session_state


def test_sessao_ausente_nao_carrega_dados(tela):
    interface, cliente, conta = tela
    interface.session_state.clear()
    pagina.renderizar(cliente, conta)
    assert interface.erros == ["Sua sessão expirou. Entre novamente para consultar os Profissionais."]
    cliente.listar_opcoes_agenda.assert_not_called()
