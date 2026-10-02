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
