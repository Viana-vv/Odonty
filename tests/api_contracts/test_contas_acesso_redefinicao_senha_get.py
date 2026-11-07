import pytest

from conftest import resposta
from sorrisomais.api_redefinicao_senha import ClienteRedefinicaoSenha, ErroRedefinicaoSenha, ERROS_CONSULTA
from test_contas_acesso_redefinicoes_senha_post import OPERACAO, PROJECAO


@pytest.mark.parametrize("envio", ["processando", "aceito", "falhou", "desconhecido"])
@pytest.mark.parametrize("link", ["pendente", "ativo", "consumido", "expirado", "substituido", "invalidado"])
def test_consulta_preserva_estados_datas_passadas(cliente, http, envio, link):
    dados = {**PROJECAO, "estado_envio": envio, "estado_link": link}
    http.return_value = resposta(dados)
    if (link == "pendente" and envio != "processando"
            or link == "ativo" and envio not in {"aceito", "desconhecido"}):
        with pytest.raises(ErroRedefinicaoSenha):
            ClienteRedefinicaoSenha(cliente.configuracao).consultar("sessao-ficticia", 7, OPERACAO)
        return
    assert ClienteRedefinicaoSenha(cliente.configuracao).consultar("sessao-ficticia", 7, OPERACAO) == dados
    args, kwargs = http.call_args
    assert args[0] == "GET" and args[1].endswith("/" + OPERACAO)
    assert kwargs["json"] is None and "params" not in kwargs
    assert http.call_count == 1


@pytest.mark.parametrize("status,codigo", [(s, c) for s, cs in ERROS_CONSULTA.items() for c in cs])
def test_erros_consulta_nunca_criam(cliente, http, status, codigo):
    http.return_value = resposta({"codigo": codigo, "mensagem": "segredo-remoto"}, status)
    with pytest.raises(ErroRedefinicaoSenha) as falha:
        ClienteRedefinicaoSenha(cliente.configuracao).consultar("sessao-ficticia", 7, OPERACAO)
    assert (falha.value.status, falha.value.codigo) == (status, codigo)
    assert not falha.value.resultado_incerto
    assert http.call_count == 1 and http.call_args.args[0] == "GET"
    assert "segredo-remoto" not in repr(falha.value)


@pytest.mark.parametrize("dados", [None, [], {}, {**PROJECAO, "senha": "segredo"}, {**PROJECAO, "expira_em": None}])
def test_consulta_malformada(cliente, http, dados):
    http.return_value = resposta(dados)
    with pytest.raises(ErroRedefinicaoSenha):
        ClienteRedefinicaoSenha(cliente.configuracao).consultar("sessao-ficticia", 7, OPERACAO)
    assert http.call_count == 1


def test_data_no_limite_do_datetime_erro_sanitizado(cliente, http):
    http.return_value = resposta({**PROJECAO, "criada_em": "9999-12-31T23:59:59.999Z"})
    with pytest.raises(ErroRedefinicaoSenha) as falha:
        ClienteRedefinicaoSenha(cliente.configuracao).consultar("sessao-ficticia", 7, OPERACAO)
    assert not falha.value.resultado_incerto
