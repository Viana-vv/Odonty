import pytest

from conftest import resposta
from sorrisomais.api import ErroAcesso


PACIENTE = {
    "id": 19, "nome": "Paciente Fictício", "data_nascimento": "2000-02-29",
    "cpf": "529.982.247-25", "telefone": "(11) 90000-0000",
    "celular": "(11) 91111-2222", "email": "PESSOA@example.com",
}


def test_get_paciente_envia_id_e_normaliza_resposta_sem_rede(cliente, http):
    http.return_value = resposta({"paciente": PACIENTE})

    assert cliente.obter_paciente("token-ficticio", 19) == {
        "id": 19, "nome": "Paciente Fictício", "data_nascimento": "2000-02-29",
        "cpf": "52998224725", "telefone": "11900000000",
        "celular": "11911112222", "email": "pessoa@example.com",
    }
    assert http.call_args.args[:2] == ("GET", "https://exemplo.invalid/api:teste/pacientes/19")
    assert http.call_args.kwargs["headers"]["Authorization"] == "Bearer token-ficticio"


@pytest.mark.parametrize("status", [401, 403, 404, 429, 503])
def test_get_paciente_mapeia_erros_sem_expor_resposta(cliente, http, status):
    http.return_value = resposta({"mensagem": "DADO_PESSOAL"}, status)

    with pytest.raises(ErroAcesso) as erro:
        cliente.obter_paciente("token-ficticio", 19)

    assert "DADO_PESSOAL" not in str(erro.value)


def test_get_paciente_rejeita_resposta_incompativel(cliente, http):
    http.return_value = resposta({"paciente": {**PACIENTE, "id": 20}})

    with pytest.raises(ErroAcesso):
        cliente.obter_paciente("token-ficticio", 19)


def test_get_paciente_nao_chama_api_com_id_invalido(cliente, http):
    with pytest.raises(ValueError):
        cliente.obter_paciente("token-ficticio", 0)
    http.assert_not_called()
