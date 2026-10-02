import pytest

from conftest import resposta
from sorrisomais.contratos_clinicos import DadosContratoInvalidos


def test_patch_consultas_situacao_envia_somente_mudanca_pedida(cliente, http):
    http.return_value = resposta({"consulta": {
        "id": 9, "paciente_id": 4, "profissional_id": 8,
        "disponibilidade_id": 3, "situacao": "Cancelada",
    }})
    resultado = cliente.atualizar_situacao_consulta(
        "token-ficticio", 9, "Cancelada", "Paciente solicitou cancelamento",
    )
    assert resultado["situacao"] == "Cancelada"
    assert http.call_args.args[:2] == (
        "PATCH", "https://exemplo.invalid/api:teste/consultas/9/situacao",
    )
    assert http.call_args.kwargs["json"] == {
        "situacao": "Cancelada", "motivo_cancelamento": "Paciente solicitou cancelamento",
    }


def test_patch_consultas_situacao_exige_motivo_para_cancelar(cliente, http):
    with pytest.raises(DadosContratoInvalidos):
        cliente.atualizar_situacao_consulta("token-ficticio", 9, "Cancelada")
    http.assert_not_called()
