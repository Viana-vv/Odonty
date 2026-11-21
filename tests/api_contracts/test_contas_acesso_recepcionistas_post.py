from pathlib import Path

import pytest
import requests

from sorrisomais.api import ErroAcesso
from conftest import BASE, resposta


ROTA = "/contas-acesso/recepcionistas"
SENHA = " senha-ficticia "
CONTA = {
    "id": 23, "nome": "Pessoa Fictícia", "email": "equipe@example.invalid",
    "perfis": ["recepcionista"], "situacao": "ativo",
}


def cadastrar(cliente):
    return cliente.cadastrar_recepcionista(
        "token-ficticio", " Pessoa Fictícia ", " EQUIPE@EXAMPLE.INVALID ", SENHA,
    )


def test_cadastro_envia_somente_dados_previstos(cliente, http):
    http.return_value = resposta({"conta": CONTA}, 201)
    assert cadastrar(cliente) == 23
    http.assert_called_once()
    args, kwargs = http.call_args
    assert args == ("POST", BASE + ROTA)
    assert kwargs["headers"]["Authorization"] == "Bearer token-ficticio"
    assert kwargs["json"] == {"nome": CONTA["nome"], "email": CONTA["email"], "senha": SENHA}


@pytest.mark.parametrize("token,nome,email,senha,status", [
    ("", "Pessoa Fictícia", CONTA["email"], SENHA, 401),
    ("token", "X", CONTA["email"], SENHA, 400),
    ("token", "X" * 121, CONTA["email"], SENHA, 400),
    ("token", CONTA["nome"], "email inválido", SENHA, 400),
    ("token", CONTA["nome"], "x" * 245 + "@example.invalid", SENHA, 400),
    ("token", CONTA["nome"], CONTA["email"], "x" * 11, 400),
    ("token", CONTA["nome"], CONTA["email"], "x" * 129, 400),
])
def test_rejeita_dados_invalidos_antes_do_post(cliente, http, token, nome, email, senha, status):
    with pytest.raises(ErroAcesso) as erro:
        cliente.cadastrar_recepcionista(token, nome, email, senha)
    assert erro.value.status == status
    http.assert_not_called()


@pytest.mark.parametrize("status", [400, 401, 403, 409, 429, 503])
def test_erros_do_xano_nao_expoem_corpo_nem_repetem_post(cliente, http, status):
    http.return_value = resposta({"mensagem": SENHA}, status)
    with pytest.raises(ErroAcesso) as erro:
        cadastrar(cliente)
    assert erro.value.status == status
    assert SENHA not in str(erro.value)
    if status == 409:
        assert str(erro.value) == "E-mail já cadastrado."
    http.assert_called_once()


@pytest.mark.parametrize("conta", [
    {}, CONTA | {"perfis": ["administrador"]}, CONTA | {"senha": SENHA},
    CONTA | {"id": True}, CONTA | {"situacao": "inativo"},
])
def test_resposta_incompativel_e_tratada_como_resultado_incerto(cliente, http, conta):
    http.return_value = resposta({"conta": conta}, 201)
    with pytest.raises(ErroAcesso, match="Confira a lista de Contas de Acesso"):
        cadastrar(cliente)
    http.assert_called_once()


def test_timeout_nao_repete_post(cliente, http):
    http.side_effect = requests.Timeout()
    with pytest.raises(ErroAcesso, match="Não foi possível confirmar"):
        cadastrar(cliente)
    http.assert_called_once()


def test_export_xano_restringe_criacao_e_projecao():
    caminho = (Path(__file__).resolve().parents[2] / "backend/xano/api/sorriso_acesso"
               / "contas_acesso_recepcionistas_POST.xs")
    fonte = caminho.read_text(encoding="utf-8")
    assert 'query "contas-acesso/recepcionistas" verb=POST' in fonte
    assert 'auth = "conta_acesso"' in fonte
    assert 'perfis|intersect:["administrador"]' in fonte
    assert fonte.index("sorriso_validar_sessao") < fonte.index("db.add conta_acesso")
    resposta_xano = fonte.split("  response = ", 1)[1].split("  history", 1)[0]
    assert "conta: {" in resposta_xano
    assert "senha" not in resposta_xano
    assert "token" not in resposta_xano
    assert {linha.strip().split(":", 1)[0] for linha in resposta_xano.splitlines()
            if ":" in linha} == {"conta", "id", "nome", "email", "perfis", "situacao"}
    assert 'history = false' in fonte
