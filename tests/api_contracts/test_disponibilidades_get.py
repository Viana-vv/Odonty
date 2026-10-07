from sorrisomais.api import ErroAcesso
from datetime import timedelta

import pytest

from conftest import FUTURO, resposta


def test_get_disponibilidades_envia_filtros_e_valida_resposta(cliente, http):
    http.return_value = resposta({"disponibilidades": [{
        "id": 3, "profissional_id": 8, "inicio": FUTURO.isoformat(),
        "fim": (FUTURO + timedelta(hours=1)).isoformat(), "situacao": "disponivel",
    }]})
    resultado = cliente.listar_disponibilidades(
        "token-ficticio", 8, FUTURO.isoformat(), (FUTURO + timedelta(hours=1)).isoformat(),
    )
    assert resultado[0]["id"] == 3
    assert resultado[0]["inicio"] == FUTURO.isoformat()
    assert resultado[0]["fim"] == (FUTURO + timedelta(hours=1)).isoformat()
    assert http.call_args.args[:2] == ("GET", "https://exemplo.invalid/api:teste/disponibilidades")
    assert http.call_args.kwargs["params"] == {
        "profissional_id": 8, "inicio": FUTURO.isoformat(),
        "fim": (FUTURO + timedelta(hours=1)).isoformat(),
    }


def test_get_disponibilidades_rejeita_filtro_parcial_sem_rede(cliente, http):
    from sorrisomais.contratos_clinicos import DadosContratoInvalidos

    with pytest.raises(DadosContratoInvalidos):
        cliente.listar_disponibilidades("token-ficticio", inicio=FUTURO.isoformat())
    http.assert_not_called()


def test_get_disponibilidades_rejeita_resposta_incompativel(cliente, http):
    http.return_value = resposta({"disponibilidades": [{"id": 3}]})
    with pytest.raises(ErroAcesso):
        cliente.listar_disponibilidades("token-ficticio")
