from uuid import uuid4

import pytest

from sorrisomais.api import ErroAcesso
from conftest import resposta


def dados(operacao_id):
    return {
        "nome": "Paciente Fictício", "data_nascimento": "2000-02-29",
        "telefone": "(11) 90000-0000", "cpf": "987.000.000-27",
        "email": "PESSOA@example.com", "celular": "(11) 91111-2222",
        "operacao_id": operacao_id,
    }


def test_post_pacientes_envia_payload_normalizado_e_idempotente(cliente, http):
    operacao_id = str(uuid4())
    http.return_value = resposta({
        "paciente": {"id": 19, "nome": "Paciente Fictício", "situacao": "ativo"},
        "operacao_id": operacao_id,
    }, 201)
    assert cliente.cadastrar_paciente("token-ficticio", **dados(operacao_id)) == 19
    assert http.call_args.args[:2] == ("POST", "https://exemplo.invalid/api:teste/pacientes")
    assert http.call_args.kwargs["json"] == {
        "nome": "Paciente Fictício", "data_nascimento": "2000-02-29",
        "telefone": "11900000000", "cpf": "98700000027", "email": "pessoa@example.com",
        "celular": "11911112222", "operacao_id": operacao_id,
    }


def test_post_pacientes_nao_confirma_operacao_diferente(cliente, http):
    http.return_value = resposta({
        "paciente": {"id": 19, "nome": "Paciente Fictício", "situacao": "ativo"},
        "operacao_id": str(uuid4()),
    }, 201)
    with pytest.raises(ErroAcesso, match="confirmar"):
        cliente.cadastrar_paciente("token-ficticio", **dados(str(uuid4())))


@pytest.mark.parametrize("status,codigo", [(400, None), (401, None), (403, None), (409, "CPF_DUPLICADO"), (429, None), (503, None)])
def test_post_pacientes_mapeia_erros_sem_expor_resposta(cliente, http, status, codigo):
    http.return_value = resposta({"codigo": codigo, "mensagem": "DADO_SENSIVEL"}, status)
    with pytest.raises(ErroAcesso) as erro:
        cliente.cadastrar_paciente("token-ficticio", **dados(str(uuid4())))
    assert "DADO_SENSIVEL" not in str(erro.value)
