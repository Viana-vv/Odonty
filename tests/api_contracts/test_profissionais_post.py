from pathlib import Path

import pytest

from sorrisomais.api import ErroAcesso
from conftest import resposta


def test_post_profissionais_normaliza_payload_e_valida_vinculos(cliente, http):
    http.return_value = resposta({
        "profissional": {
            "id": 8, "nome": "Profissional Fictício", "cro": "SP-123456", "situacao": "ativo",
            "especialidade": {"id": 2, "nome": "Ortodontia"},
        },
        "conta": {"id": 12, "situacao": "ativo", "perfis": ["profissional"]},
    }, 201)
    result = cliente.cadastrar_profissional(
        "token-ficticio", " Profissional Fictício ", "DENTISTA@example.com",
        "senha-ficticia-segura", "sp-0123456", 2,
    )
    assert result == 8
    assert http.call_args.args[:2] == ("POST", "https://exemplo.invalid/api:teste/profissionais")
    assert http.call_args.kwargs["json"] == {
        "nome": "Profissional Fictício", "email": "dentista@example.com",
        "senha": "senha-ficticia-segura", "cro": "SP-123456", "especialidade_id": 2,
    }


@pytest.mark.parametrize("resposta_corrompida", [
    {"profissional": None, "conta": {}},
    {"profissional": {"id": True}, "conta": {"id": 1}},
    {"profissional": {"id": 8, "nome": "Outra pessoa"}, "conta": {"id": 12}},
])
def test_post_profissionais_rejeita_resposta_incompativel(cliente, http, resposta_corrompida):
    http.return_value = resposta(resposta_corrompida, 201)
    with pytest.raises(ErroAcesso, match="confirmar"):
        cliente.cadastrar_profissional(
            "token-ficticio", "Profissional Fictício", "dentista@example.com",
            "senha-ficticia-segura", "SP-123456", 2,
        )


def test_export_xano_profissionais_valida_admin_e_cria_vinculo_atomico():
    arquivo = (Path(__file__).resolve().parents[2]
               / "backend" / "xano" / "api" / "sorriso_acesso" / "profissionais_POST.xs")
    codigo = arquivo.read_text(encoding="utf-8-sig")
    assert 'auth = "conta_acesso"' in codigo
    assert "function.run sorriso_validar_sessao" in codigo
    assert 'perfis|intersect:["administrador"]' in codigo
    assert '"HTTP/1.1 403 Forbidden"' in codigo
    assert '"HTTP/1.1 400 Bad Request"' in codigo
    assert '"HTTP/1.1 409 Conflict"' in codigo
    assert "db.transaction" in codigo
    assert "db.add conta_acesso" in codigo
    assert 'perfis: ["profissional"]' in codigo
    assert "db.add profissional" in codigo
    assert 'Cache-Control: no-store' in codigo
    assert "history = false" in codigo
    resposta = codigo.split("\n  response = {", 1)[1].split("\n  history = false", 1)[0]
    assert all(segredo not in resposta.lower() for segredo in ("senha", "email", "token"))
