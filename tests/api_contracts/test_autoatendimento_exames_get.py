import pytest
from pathlib import Path

from conftest import resposta
from sorrisomais.exames_api import ClienteExames


def test_get_exames_paciente_envia_requisicao_sem_identificador_de_paciente(cliente, http):
    http.return_value = resposta({"exames": [{
        "id": 9, "paciente_id": 4, "consulta_id": 2, "tipo": "Exame fictício",
        "situacao": "Resultado disponível", "solicitado_em": "2026-10-01T10:00:00Z",
        "realizado_em": "2026-10-02T10:00:00Z", "resultado": "Resultado fictício",
    }]})

    exames = ClienteExames(cliente).listar("token-ficticio")

    assert exames[0]["resultado"] == "Resultado fictício"
    assert http.call_args.args[:2] == ("GET", "https://exemplo.invalid/api:teste/exames")
    assert http.call_args.kwargs["params"] is None
    assert http.call_args.kwargs["headers"]["Authorization"] == "Bearer token-ficticio"
