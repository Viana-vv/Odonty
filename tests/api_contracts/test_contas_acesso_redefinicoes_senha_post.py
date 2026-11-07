import pytest
import requests

from conftest import resposta
from sorrisomais.api_redefinicao_senha import ClienteRedefinicaoSenha, ErroRedefinicaoSenha, ERROS_SOLICITACAO

OPERACAO = "019a5be0-0000-7000-8000-000000000001"
PROJECAO = {
    "operacao_id": OPERACAO, "criada_em": "2026-01-01T00:00:00.000Z",
    "consultavel_ate": "2026-01-31T00:00:00.000Z", "expira_em": "2026-01-01T00:15:00.000Z",
    "envio_limite_em": "2026-01-01T00:00:20.000Z", "estado_envio": "aceito", "estado_link": "expirado",
}


def test_solicita_corpo_exato_sem_retry(cliente, http):
    http.return_value = resposta(PROJECAO)
    api = ClienteRedefinicaoSenha(cliente.configuracao)
    assert api.solicitar("sessao-ficticia", 7, OPERACAO) == PROJECAO
    assert http.call_count == 1
    args, kwargs = http.call_args
    assert args[0] == "POST" and args[1].endswith("/contas-acesso/7/redefinicoes-senha")
    assert kwargs["json"] == {"operacao_id": OPERACAO}
    assert kwargs["allow_redirects"] is False


@pytest.mark.parametrize("status,codigo", [(s, c) for s, cs in ERROS_SOLICITACAO.items() for c in cs])
def test_erros_conhecidos_sanitizados(cliente, http, status, codigo):
    http.return_value = resposta({"codigo": codigo, "mensagem": "segredo-remoto"}, status)
    http.return_value.headers = {"Retry-After": "60"}
    with pytest.raises(ErroRedefinicaoSenha) as falha:
        ClienteRedefinicaoSenha(cliente.configuracao).solicitar("sessao-ficticia", 7, OPERACAO)
    assert (falha.value.status, falha.value.codigo) == (status, codigo)
    assert not falha.value.resultado_incerto
    assert "segredo-remoto" not in repr(falha.value)
    if status == 429:
        assert falha.value.retry_after == 60


@pytest.mark.parametrize("alteracao", [{"token": "segredo"}, {"estado_envio": "entregue"},
    {"criada_em": "2026-01-01T00:00:00Z"}, {"estado_link": []}, {"consultavel_ate": "2026-02-01T00:00:00.000Z"}])
def test_projecao_invalida_incerta(cliente, http, alteracao):
    http.return_value = resposta({**PROJECAO, **alteracao})
    with pytest.raises(ErroRedefinicaoSenha) as falha:
        ClienteRedefinicaoSenha(cliente.configuracao).solicitar("sessao-ficticia", 7, OPERACAO)
    assert falha.value.resultado_incerto


@pytest.mark.parametrize("operacao", [OPERACAO.upper(), "019a5be0-0000-4000-8000-000000000001", "invalida"])
def test_uuid_invalido_sem_rede(cliente, http, operacao):
    with pytest.raises(ErroRedefinicaoSenha):
        ClienteRedefinicaoSenha(cliente.configuracao).solicitar("sessao-ficticia", 7, operacao)
    http.assert_not_called()


def test_timeout_nao_repete(cliente, http):
    http.side_effect = requests.Timeout("segredo-remoto")
    with pytest.raises(ErroRedefinicaoSenha) as falha:
        ClienteRedefinicaoSenha(cliente.configuracao).solicitar("sessao-ficticia", 7, OPERACAO)
    assert falha.value.resultado_incerto and http.call_count == 1
    assert "segredo" not in repr(falha.value)


@pytest.mark.parametrize("alteracao", [
    {"criada_em": "9999-12-31T23:59:59.999Z"},
    {"envio_limite_em": "2026-01-01T00:00:30.001Z"},
    {"envio_limite_em": "2026-01-01T00:00:00.000Z"},
    {"estado_envio": "processando", "estado_link": "ativo"},
    {"estado_envio": "falhou", "estado_link": "ativo"},
    {"estado_envio": "aceito", "estado_link": "pendente"},
])
def test_projecao_incompativel_ou_overflow_incerto(cliente, http, alteracao):
    http.return_value = resposta({**PROJECAO, **alteracao})
    with pytest.raises(ErroRedefinicaoSenha) as falha:
        ClienteRedefinicaoSenha(cliente.configuracao).solicitar("sessao-ficticia", 7, OPERACAO)
    assert falha.value.resultado_incerto


def test_deadline_maximo_inclusivo(cliente, http):
    dados = {**PROJECAO, "envio_limite_em": "2026-01-01T00:00:30.000Z"}
    http.return_value = resposta(dados)
    assert ClienteRedefinicaoSenha(cliente.configuracao).solicitar("sessao-ficticia", 7, OPERACAO) == dados
