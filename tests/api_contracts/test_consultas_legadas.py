from conftest import resposta


def test_get_consultas_preserva_consulta_legada_sem_disponibilidade(cliente, http):
    http.return_value = resposta({"consultas": [{
        "id": 13, "paciente_id": 4, "profissional_id": 8,
        "disponibilidade_id": None, "situacao": "Realizada",
        "inicio_em": "2026-09-15T10:00:00-03:00", "fim_em": "2026-09-15T10:45:00-03:00",
        "paciente_nome": "Paciente Histórico Fictício", "profissional_nome": "Profissional Histórico Fictício",
        "procedimento_nome": None, "procedimento_vinculado_nome": None,
    }]})

    consultas = cliente.listar_consultas("token-ficticio", paciente_id=4)

    assert consultas == [{
        "id": 13, "paciente_id": 4, "profissional_id": 8,
        "disponibilidade_id": None, "situacao": "Realizada",
        "inicio_em": "2026-09-15T10:00:00-03:00", "fim_em": "2026-09-15T10:45:00-03:00",
        "paciente_nome": "Paciente Histórico Fictício", "profissional_nome": "Profissional Histórico Fictício",
        "procedimentos": [],
    }]


def test_patch_consulta_legada_preserva_resposta_sem_disponibilidade(cliente, http):
    http.return_value = resposta({"consulta": {
        "id": 13, "paciente_id": 4, "profissional_id": 8,
        "disponibilidade_id": None, "situacao": "Cancelada",
    }})

    consulta = cliente.atualizar_situacao_consulta(
        "token-ficticio", 13, "Cancelada", "Solicitação recebida pela clínica",
    )

    assert consulta["disponibilidade_id"] is None
