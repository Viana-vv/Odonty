from datetime import timedelta

import pytest

from conftest import FUTURO, resposta
from sorrisomais.contratos_clinicos import DadosContratoInvalidos


def test_patch_disponibilidades_altera_situacao_sem_rede_real(cliente, http):
    inicio = FUTURO.isoformat()
    fim = (FUTURO + timedelta(hours=1)).isoformat()
    http.return_value = resposta({"disponibilidade": {
        "id": 15, "profissional_id": 8, "inicio": inicio, "fim": fim,
        "situacao": "bloqueado",
    }})

    resultado = cliente.atualizar_disponibilidade(
        "token-ficticio", 15, situacao="bloqueado",
    )

    assert resultado["situacao"] == "bloqueado"
    assert resultado["inicio"] == inicio
    assert resultado["fim"] == fim
    assert http.call_args.args[:2] == (
        "PATCH", "https://exemplo.invalid/api:teste/disponibilidades/15",
    )
    assert http.call_args.kwargs["json"] == {"situacao": "bloqueado"}


@pytest.mark.parametrize("situacao", ["reservado", "indisponivel", "livre"])
def test_patch_disponibilidades_rejeita_situacao_controlada_pelo_backend(cliente, http, situacao):
    with pytest.raises(DadosContratoInvalidos):
        cliente.atualizar_disponibilidade("token-ficticio", 15, situacao=situacao)
    http.assert_not_called()


def test_patch_disponibilidades_exige_campo_sem_vazio(cliente, http):
    with pytest.raises(DadosContratoInvalidos):
        cliente.atualizar_disponibilidade("token-ficticio", 15)
    http.assert_not_called()
