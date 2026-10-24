from pathlib import Path

import pytest

from sorrisomais import api_contas_acesso
from sorrisomais.api import ErroAcesso
from conftest import resposta


def conta_ficticia(**extras):
    return {
        "id": 12,
        "nome": "Ana Administradora Fictícia",
        "email": "ana@example.invalid",
        "perfis": ["administrador"],
        "situacao": "ativo",
        **extras,
    }


def test_get_contas_acesso_envia_rota_e_token_e_retem_apenas_campos_permitidos(cliente, http):
    http.return_value = resposta({"contas_acesso": [conta_ficticia(senha="HASH-NAO-RETORNAR", token="SEGREDO")]})

    resultado = api_contas_acesso.listar_contas_acesso(cliente, "token-ficticio")

    assert resultado == [{
        "id": 12,
        "nome": "Ana Administradora Fictícia",
        "email": "ana@example.invalid",
        "perfis": ["administrador"],
        "situacao": "ativo",
    }]
    assert http.call_args.args[:2] == ("GET", "https://exemplo.invalid/api:teste/contas-acesso")
    assert http.call_args.kwargs["headers"]["Authorization"] == "Bearer token-ficticio"


@pytest.mark.parametrize("payload", [
    {},
    {"contas_acesso": [{"id": "12"}]},
    {"contas_acesso": [{**conta_ficticia(), "perfis": ["desconhecido"]}]},
    {"contas_acesso": [{**conta_ficticia(), "perfis": [{}]}]},
    {"contas_acesso": [{**conta_ficticia(), "situacao": "removido"}]},
])
def test_get_contas_acesso_rejeita_resposta_fora_do_contrato(cliente, http, payload):
    http.return_value = resposta(payload)

    with pytest.raises(ErroAcesso):
        api_contas_acesso.listar_contas_acesso(cliente, "token-ficticio")


def test_export_get_contas_acesso_tem_autorizacao_e_projection_estrita():
    path = Path(__file__).resolve().parents[2] / "backend/xano/api/sorriso_acesso/contas_acesso_GET.xs"
    source = path.read_text(encoding="utf-8-sig")
    assert 'auth = "conta_acesso"' in source
    assert "function.run sorriso_validar_sessao" in source
    assert 'intersect:["administrador", "recepcionista"]' in source
    assert 'output = ["id", "nome", "email", "perfis", "situacao"]' in source
    assert 'response = {contas_acesso: $resultado}' in source
    for proibido in ('"senha"', '"token"', '"hash"', '"cpf"'):
        assert proibido not in source
