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


def test_export_get_filtra_no_xano_por_escopo_obrigatorio():
    raiz = Path(__file__).resolve().parents[2]
    export = (raiz / "backend/xano/api/sorriso_acesso/registros_clinicos_GET.xs").read_text(encoding="utf-8")

    assert 'auth = "conta_acesso"' in export
    assert "function.run sorriso_validar_sessao" in export
    assert '$db.registro_clinico.profissional_id == $profissional_escopo' in export
    assert '$db.registro_clinico.paciente_id == $paciente_escopo && $db.registro_clinico.liberado_paciente == true' in export
    assert '$registro.paciente_id != $input.paciente_id' in export
    assert '$registro.consulta_id != $input.consulta_id' in export
    assert 'history = false' in export
    where_clauses = [linha.split("where =", 1)[1] for linha in export.splitlines() if "where =" in linha]
    assert len(where_clauses) == 2
    assert all("== null ||" not in clausula for clausula in where_clauses)
