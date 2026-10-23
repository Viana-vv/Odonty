from pathlib import Path

import pytest

from sorrisomais.api import ErroAcesso
from conftest import resposta


def test_get_profissionais_valida_campos_permitidos(cliente, http):
    http.return_value = resposta({"profissionais": [{
        "id": 201, "nome": "Dra. Exemplo", "cro": "SP-123",
        "especialidade": {"id": 3, "nome": "Ortodontia"},
        "email": "exemplo@clinica.invalid", "telefone": None,
        "situacao": "inativo", "cpf": "NAO-RETORNAR",
    }]})
    assert cliente.listar_profissionais("token-ficticio") == [{
        "id": 201, "nome": "Dra. Exemplo", "cro": "SP-123",
        "especialidade": {"id": 3, "nome": "Ortodontia"},
        "email": "exemplo@clinica.invalid", "telefone": None,
        "situacao": "inativo",
    }]
    assert http.call_args.args[:2] == ("GET", "https://exemplo.invalid/api:teste/profissionais")


def test_get_profissionais_rejeita_contrato_invalido(cliente, http):
    http.return_value = resposta({"profissionais": [{"id": 201, "nome": "Dra. Exemplo"}]})
    with pytest.raises(ErroAcesso):
        cliente.listar_profissionais("token-ficticio")


def test_export_get_profissionais_restringe_campos_e_autorizacao():
    path = Path(__file__).resolve().parents[2] / "backend/xano/api/sorriso_acesso/profissionais_GET.xs"
    source = path.read_text(encoding="utf-8-sig")
    assert 'auth = "conta_acesso"' in source
    assert "function.run sorriso_validar_sessao" in source
    assert 'intersect:["administrador", "recepcionista"]' in source
    assert '"cpf"' not in source and '"conta_acesso_id"' not in source
    assert 'response = {profissionais: $resultado}' in source
