import pytest

from pathlib import Path

from sorrisomais.api import ErroAcesso
from conftest import resposta


def test_get_especialidades_envia_bearer_e_valida_resultado(cliente, http):
    http.return_value = resposta({"especialidades": [{"id": 2, "nome": "Ortodontia"}]})
    assert cliente.listar_especialidades("token-ficticio") == [{"id": 2, "nome": "Ortodontia"}]
    assert http.call_args.args[:2] == ("GET", "https://exemplo.invalid/api:teste/especialidades")
    assert http.call_args.kwargs["headers"]["Authorization"] == "Bearer token-ficticio"


def test_get_especialidades_retorna_lista_vazia(cliente, http):
    http.return_value = resposta({"especialidades": []})
    assert cliente.listar_especialidades("token-ficticio") == []


def test_export_xano_especialidades_exige_sessao_administrativa():
    arquivo = (Path(__file__).resolve().parents[2]
               / "backend" / "xano" / "api" / "sorriso_acesso" / "especialidades_GET.xs")
    codigo = arquivo.read_text(encoding="utf-8-sig")
    assert 'auth = "conta_acesso"' in codigo
    assert "function.run sorriso_validar_sessao" in codigo
    assert 'perfis|intersect:["administrador"]' in codigo
    assert '$db.especialidade.ativo == true' in codigo
    assert 'Cache-Control: no-store' in codigo
    assert "history = false" in codigo


@pytest.mark.parametrize("itens", [None, {}, [{"id": True, "nome": "A"}], [{"id": 1, "nome": ""}]])
def test_get_especialidades_rejeita_resposta_invalida(cliente, http, itens):
    http.return_value = resposta({"especialidades": itens})
    with pytest.raises(ErroAcesso):
        cliente.listar_especialidades("token-ficticio")
