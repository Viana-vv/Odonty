"""Verificações simuladas; não substituem integração contra Xano."""

from datetime import datetime, timedelta, timezone
from unittest.mock import Mock

import pytest
import requests

from sorrisomais.api import ClienteXano, ContaAcesso, Credencial, ErroAcesso, ler_validade
from sorrisomais.config import Configuracao, ConfiguracaoInvalida
from sorrisomais import sessao

FUTURO = (datetime.now(timezone.utc) + timedelta(hours=1)).replace(microsecond=0)


def resposta(payload=None, status=200):
    r = Mock(status_code=status)
    r.__enter__ = Mock(return_value=r)
    r.__exit__ = Mock(return_value=False)
    r.json.return_value = payload
    return r


@pytest.fixture
def cliente():
    return ClienteXano(Configuracao("https://exemplo.invalid/api:teste", 2))


@pytest.fixture
def http(monkeypatch):
    mock = Mock()
    monkeypatch.setattr(requests, "request", mock)
    return mock


def identidade(perfis=None):
    return {"conta": {"id": 1, "nome": "Pessoa Fictícia", "perfis": perfis or ["profissional"], "situacao": "ativo"}, "expira_em": FUTURO.isoformat()}


@pytest.mark.parametrize("url", ["", "http://exemplo.com/api", "https://token@exemplo.com/api", "https://exemplo.com/api?token=segredo", "https://exemplo.com/api#segredo", "https://exemplo.com:erro/api"])
def test_configuracao_rejeita_endereco_inseguro(monkeypatch, url):
    monkeypatch.setenv("XANO_API_BASE_URL", url)
    with pytest.raises(ConfiguracaoInvalida):
        Configuracao.do_ambiente()


@pytest.mark.parametrize("timeout", ["nan", "inf", "0", "-1", "texto"])
def test_configuracao_rejeita_timeout(monkeypatch, timeout):
    monkeypatch.setenv("XANO_API_BASE_URL", "https://exemplo.invalid/api:teste")
    monkeypatch.setenv("XANO_HTTP_TIMEOUT_SECONDS", timeout)
    with pytest.raises(ConfiguracaoInvalida):
        Configuracao.do_ambiente()


@pytest.mark.parametrize("email,senha", [("", ""), ("ficticio@example.com", ""), ("sem-arroba", "ficticia"), ("a @example.com", "ficticia")])
def test_campos_invalidos_nao_chamam_api(cliente, http, email, senha):
    with pytest.raises(ErroAcesso):
        cliente.entrar(email, senha)
    http.assert_not_called()


def test_login_envia_senha_sem_transformacao(cliente, http):
    http.return_value = resposta({"token": "token-simulado", "tipo_token": "Bearer", "expira_em": FUTURO.isoformat()})
    cred = cliente.entrar(" TESTE@example.com ", " senha fictícia ")
    assert http.call_args.kwargs["json"] == {"email": "teste@example.com", "senha": " senha fictícia "}
    assert http.call_args.kwargs["allow_redirects"] is False
    assert http.call_args.kwargs["timeout"] == 2
    assert "token-simulado" not in repr(cred)


@pytest.mark.parametrize("status", [400, 401, 403, 429, 500, 503, 302])
def test_erros_nao_expoem_resposta(cliente, http, status):
    http.return_value = resposta({"mensagem": "SEGREDO_NAO_EXIBIR"}, status)
    with pytest.raises(ErroAcesso) as e:
        cliente.entrar("teste@example.com", "senha-fictícia")
    assert "SEGREDO" not in str(e.value)


@pytest.mark.parametrize("error", [requests.Timeout, requests.ConnectionError])
def test_falha_rede_segura(cliente, http, error):
    http.side_effect = error("token=NAO_EXIBIR")
    with pytest.raises(ErroAcesso) as e:
        cliente.identificar("ficticio")
    assert "NAO_EXIBIR" not in str(e.value)


@pytest.mark.parametrize("data", [None, [], {}, {"token": "t", "tipo_token": "Errado"}, {"token": "a\nb", "tipo_token": "Bearer"}])
def test_respostas_login_invalidas(cliente, http, data):
    http.return_value = resposta(data)
    with pytest.raises(ErroAcesso):
        cliente.entrar("teste@example.com", "ficticia")


def test_resposta_nao_json(cliente, http):
    http.return_value = resposta()
    http.return_value.json.side_effect = ValueError("corpo-sensivel")
    with pytest.raises(ErroAcesso):
        cliente.identificar("ficticio")


@pytest.mark.parametrize("perfis", [["paciente"], ["inventado"], ["profissional", "profissional"], [1]])
def test_perfis_invalidos(cliente, http, perfis):
    http.return_value = resposta(identidade(perfis))
    with pytest.raises(ErroAcesso):
        cliente.identificar("ficticio")


def test_multiplos_perfis(cliente, http):
    http.return_value = resposta(identidade(["profissional", "administrador", "paciente"]))
    conta = cliente.identificar("ficticio")
    assert conta.perfis == ("administrador", "profissional")
    assert http.call_args.kwargs["headers"]["Authorization"] == "Bearer ficticio"


@pytest.mark.parametrize("data", ["2020-01-01T00:00:00Z", "2090-02-31T00:00:00Z", "2090-01-01", None])
def test_validade_invalida(data):
    with pytest.raises(ErroAcesso):
        ler_validade(data)


def test_identidade_precisa_ser_confirmada():
    client = Mock()
    client.entrar.return_value = Credencial("ficticio", FUTURO)
    client.identificar.side_effect = ErroAcesso()
    state = {}
    with pytest.raises(ErroAcesso):
        sessao.entrar(state, client, "teste@example.com", "ficticia")
    assert sessao.CHAVE not in state
    client.sair.assert_called_once_with("ficticio")


def test_sessoes_isoladas_e_identidade_revalidada():
    client = Mock()
    client.entrar.return_value = Credencial("ficticio", FUTURO)
    client.identificar.return_value = ContaAcesso(1, "Fictício", ("profissional",), FUTURO)
    a, b = {}, {}
    sessao.entrar(a, client, "teste@example.com", "ficticia")
    assert sessao.identificar(b, client) is None
    assert sessao.identificar(a, client).id == 1
    assert client.identificar.call_count == 2
    client.identificar.side_effect = ErroAcesso(status=403)
    with pytest.raises(ErroAcesso):
        sessao.identificar(a, client)
    assert not a


def test_sessao_expirada_nao_consulta_conteudo():
    client = Mock()
    state = {sessao.CHAVE: Credencial("ficticio", datetime.now(timezone.utc) - timedelta(seconds=1))}
    with pytest.raises(ErroAcesso):
        sessao.identificar(state, client)
    client.identificar.assert_not_called()
    assert not state


def test_logout_limpa_estado_mesmo_sem_rede():
    state = {sessao.CHAVE: Credencial("ficticio", FUTURO)}
    client = Mock()
    client.sair.side_effect = ErroAcesso()
    assert "não foi possível confirmar" in sessao.sair(state, client)
    assert not state


@pytest.mark.parametrize("status", [204, 401])
def test_logout_sem_corpo(cliente, http, status):
    http.return_value = resposta(status=status)
    assert cliente.sair("ficticio") is None
    http.return_value.json.assert_not_called()
