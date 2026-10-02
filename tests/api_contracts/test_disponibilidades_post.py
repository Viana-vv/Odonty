from datetime import timedelta

from conftest import FUTURO, resposta


def test_post_disponibilidades_cria_intervalo(cliente, http):
    inicio = FUTURO.isoformat()
    fim = (FUTURO + timedelta(hours=1)).isoformat()
    http.return_value = resposta({"disponibilidade": {
        "id": 15, "profissional_id": 8, "inicio": inicio, "fim": fim, "situacao": "disponivel",
    }}, 201)
    resultado = cliente.criar_disponibilidade("token-ficticio", 8, inicio, fim)
    assert resultado["id"] == 15
    assert http.call_args.args[:2] == ("POST", "https://exemplo.invalid/api:teste/disponibilidades")
    assert http.call_args.kwargs["json"] == {"profissional_id": 8, "inicio": inicio, "fim": fim}


def test_post_disponibilidades_rejeita_intervalo_invalido_sem_rede(cliente, http):
    from sorrisomais.contratos_clinicos import DadosContratoInvalidos
    import pytest

    with pytest.raises(DadosContratoInvalidos):
        cliente.criar_disponibilidade("token-ficticio", 8, "2026-10-05T10:00:00-03:00", "2026-10-05T09:00:00-03:00")
    http.assert_not_called()
