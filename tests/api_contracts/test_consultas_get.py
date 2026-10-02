from datetime import timedelta

from conftest import FUTURO, resposta


def test_get_consultas_envia_filtros_e_resposta_sem_conteudo_clinico(cliente, http):
    inicio = FUTURO.isoformat()
    fim = (FUTURO + timedelta(hours=1)).isoformat()
    http.return_value = resposta({"consultas": [{
        "id": 9, "paciente_id": 4, "profissional_id": 8,
        "disponibilidade_id": 3, "situacao": "Agendada",
        "conteudo_clinico": "não deve ser retornado",
    }]})
    resultado = cliente.listar_consultas(
        "token-ficticio", paciente_id=4, profissional_id=8, situacao="Agendada", inicio=inicio, fim=fim,
    )
    assert resultado == [{"id": 9, "paciente_id": 4, "profissional_id": 8,
                          "disponibilidade_id": 3, "situacao": "Agendada"}]
    assert http.call_args.args[:2] == ("GET", "https://exemplo.invalid/api:teste/consultas")
    assert http.call_args.kwargs["params"] == {
        "paciente_id": 4, "profissional_id": 8, "situacao": "Agendada", "inicio": inicio, "fim": fim,
    }
