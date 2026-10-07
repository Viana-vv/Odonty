from pathlib import Path

import pytest

from sorrisomais.api import ErroAcesso
from conftest import resposta


def test_get_agenda_opcoes_retorna_somente_id_e_nome(cliente, http):
    http.return_value = resposta({
        "pacientes": [{"id": 101, "nome": "Paciente Fictícia Aurora", "telefone": "FICTICIO-NAO-EXIBIR"}],
        "profissionais": [{"id": 201, "nome": "Dra. Exemplo Sorriso", "email": "NAO-EXIBIR"}],
        "procedimentos": [{"id": 301, "nome": "Avaliação fictícia", "preco": 0}],
    })
    assert cliente.listar_opcoes_agenda("token-ficticio") == {
        "pacientes": [{"id": 101, "nome": "Paciente Fictícia Aurora"}],
        "profissionais": [{"id": 201, "nome": "Dra. Exemplo Sorriso"}],
        "procedimentos": [{"id": 301, "nome": "Avaliação fictícia"}],
    }
    assert http.call_args.args[:2] == ("GET", "https://exemplo.invalid/api:teste/agenda/opcoes")
    assert http.call_args.kwargs["headers"]["Authorization"] == "Bearer token-ficticio"


def test_get_agenda_opcoes_mapeia_permissao_negada(cliente, http):
    http.return_value = resposta({"codigo": "ACESSO_NEGADO"}, 403)
    with pytest.raises(ErroAcesso) as erro:
        cliente.listar_opcoes_agenda("token-ficticio")
    assert erro.value.status == 403
    assert http.call_count == 1


def test_export_xano_agenda_opcoes_restringe_perfil_e_campos():
    caminho = (Path(__file__).resolve().parents[2] / "backend" / "xano" / "api"
               / "sorriso_acesso" / "agenda_opcoes_GET.xs")
    codigo = caminho.read_text(encoding="utf-8-sig")
    assert 'auth = "conta_acesso"' in codigo
    assert "function.run sorriso_validar_sessao" in codigo
    assert 'perfis|intersect:["administrador", "recepcionista"]' in codigo
    assert '$db.paciente.situacao == "ativo"' in codigo
    assert '$db.profissional.situacao == "Ativo"' in codigo
    assert '$db.procedimento.ativo == true' in codigo
    assert 'output = ["id", "nome"]' in codigo
    assert 'output = ["id", "cpf"' not in codigo
    assert '"telefone"' not in codigo
    assert "history = false" in codigo
