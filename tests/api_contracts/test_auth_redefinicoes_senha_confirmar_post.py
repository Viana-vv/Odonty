import pytest
import requests

from conftest import resposta
from sorrisomais.api_redefinicao_senha import ClienteRedefinicaoSenha, ErroRedefinicaoSenha, ERROS_CONFIRMACAO

CODIGO = "A" * 43
SENHA = "  senha ficticia  "


def test_204_sem_sessao_preserva_espacos(cliente, http):
    http.return_value = resposta(status=204)
    http.return_value.content = b""
    assert ClienteRedefinicaoSenha(cliente.configuracao).confirmar(CODIGO, SENHA) is None
    args, kwargs = http.call_args
    assert args[0] == "POST" and args[1].endswith("/auth/redefinicoes-senha/confirmar")
    assert kwargs["json"] == {"codigo": CODIGO, "senha": SENHA}
    assert "Authorization" not in kwargs["headers"]
    http.return_value.json.assert_not_called()


@pytest.mark.parametrize("status,codigo", [(s, c) for s, cs in ERROS_CONFIRMACAO.items() for c in cs])
def test_erros_publicos_sanitizados(cliente, http, status, codigo):
    http.return_value = resposta({"codigo": codigo, "mensagem": CODIGO + SENHA}, status)
    http.return_value.headers = {"Retry-After": "17"}
    with pytest.raises(ErroRedefinicaoSenha) as falha:
        ClienteRedefinicaoSenha(cliente.configuracao).confirmar(CODIGO, SENHA)
    assert (falha.value.status, falha.value.codigo) == (status, codigo)
    assert not falha.value.resultado_incerto
    if status in {409, 429}:
        assert falha.value.retry_after == 17
    assert CODIGO not in repr(falha.value) and SENHA not in repr(falha.value)


@pytest.mark.parametrize("codigo", [None, "", "A" * 42, "A" * 43 + "=", "B" * 43, " " + CODIGO])
def test_codigo_invalido_sem_rede(cliente, http, codigo):
    with pytest.raises(ErroRedefinicaoSenha):
        ClienteRedefinicaoSenha(cliente.configuracao).confirmar(codigo, SENHA)
    http.assert_not_called()


@pytest.mark.parametrize("senha", [None, "a" * 11, "a" * 129])
def test_politica_senha(cliente, http, senha):
    with pytest.raises(ErroRedefinicaoSenha):
        ClienteRedefinicaoSenha(cliente.configuracao).confirmar(CODIGO, senha)
    http.assert_not_called()


def test_commit_com_204_perdido_sem_repeticao(cliente, http):
    http.side_effect = requests.Timeout(CODIGO + SENHA)
    with pytest.raises(ErroRedefinicaoSenha) as falha:
        ClienteRedefinicaoSenha(cliente.configuracao).confirmar(CODIGO, SENHA)
    assert falha.value.resultado_incerto and http.call_count == 1
    assert CODIGO not in repr(falha.value) and SENHA not in repr(falha.value)


@pytest.mark.parametrize("espera", [None, "0", "-1", "1.5", "amanhã"])
def test_processamento_sem_espera_confiavel_incerto(cliente, http, espera):
    http.return_value = resposta({"codigo": "ENVIO_EM_PROCESSAMENTO", "mensagem": "erro"}, 409)
    http.return_value.headers = {"Retry-After": espera}
    with pytest.raises(ErroRedefinicaoSenha) as falha:
        ClienteRedefinicaoSenha(cliente.configuracao).confirmar(CODIGO, SENHA)
    assert falha.value.resultado_incerto and falha.value.retry_after is None


def test_204_com_corpo_inesperado_incerto(cliente, http):
    http.return_value = resposta(status=204)
    http.return_value.content = b'{"sessao":"segredo"}'
    with pytest.raises(ErroRedefinicaoSenha) as falha:
        ClienteRedefinicaoSenha(cliente.configuracao).confirmar(CODIGO, SENHA)
    assert falha.value.resultado_incerto
    assert "segredo" not in repr(falha.value)


def test_erro_json_nao_expoe_segredo(cliente, http):
    http.return_value = resposta(status=502)
    http.return_value.json.side_effect = ValueError(CODIGO)
    with pytest.raises(ErroRedefinicaoSenha) as falha:
        ClienteRedefinicaoSenha(cliente.configuracao).confirmar(CODIGO, SENHA)
    assert falha.value.resultado_incerto and CODIGO not in repr(falha.value)


@pytest.mark.parametrize("status,dados", [(200, {}), (500, {}), (400, None),
    (400, {"codigo": "LINK_INDISPONIVEL", "mensagem": "erro", "token": CODIGO})])
def test_resposta_nao_confiavel_incerta(cliente, http, status, dados):
    http.return_value = resposta(dados, status)
    with pytest.raises(ErroRedefinicaoSenha) as falha:
        ClienteRedefinicaoSenha(cliente.configuracao).confirmar(CODIGO, SENHA)
    assert falha.value.resultado_incerto and http.call_count == 1
