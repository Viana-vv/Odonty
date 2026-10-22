from pathlib import Path

from conftest import resposta


def test_get_registros_clinicos_envia_filtros_e_conteudo_somente_no_endpoint_clinico(cliente, http):
    http.return_value = resposta({"registros_clinicos": [{
        "id": 5, "paciente_id": 4, "profissional_id": 8, "prontuario_id": 6,
        "conteudo": "Registro fictício", "liberado_paciente": False,
    }]})
    resultado = cliente.listar_registros_clinicos("token-ficticio", paciente_id=4, consulta_id=9)
    assert resultado[0]["conteudo"] == "Registro fictício"
    assert http.call_args.args[:2] == (
        "GET", "https://exemplo.invalid/api:teste/registros-clinicos",
    )
    assert http.call_args.kwargs["params"] == {"paciente_id": 4, "consulta_id": 9}


def test_get_registros_clinicos_limita_paciente_a_vinculo_proprio_e_itens_liberados():
    caminho = (Path(__file__).resolve().parents[2] / "backend" / "xano" / "api"
               / "sorriso_acesso" / "registros_clinicos_GET.xs")
    codigo = caminho.read_text(encoding="utf-8-sig")

    assert 'field_name = "conta_acesso_id"' in codigo
    assert "field_value = $auth.id" in codigo
    assert "var.update $paciente_escopo { value = $paciente_autenticado.id }" in codigo
    assert '$db.registro_clinico.liberado_paciente == true' in codigo
    assert 'auth = "conta_acesso"' in codigo
