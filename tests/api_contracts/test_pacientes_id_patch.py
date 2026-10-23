import pytest

from conftest import resposta
from sorrisomais.api import ErroAcesso


def dados():
    return {
        "nome": "Paciente Fictício", "data_nascimento": "2000-02-29",
        "telefone": "(11) 90000-0000", "cpf": "529.982.247-25",
        "email": "PESSOA@example.com", "celular": "(11) 91111-2222",
    }


def paciente(dados_paciente):
    return {"id": 19, **dados_paciente}


def test_patch_paciente_envia_dados_normalizados_e_confirma_resposta(cliente, http):
    payload = {
        "nome": "Paciente Fictício", "data_nascimento": "2000-02-29",
        "telefone": "11900000000", "cpf": "52998224725",
        "email": "pessoa@example.com", "celular": "11911112222",
    }
    http.return_value = resposta({"paciente": paciente(payload)})

    assert cliente.atualizar_paciente("token-ficticio", 19, **dados()) == {
        "id": 19, **payload,
    }
    assert http.call_args.args[:2] == ("PATCH", "https://exemplo.invalid/api:teste/pacientes/19")
    assert http.call_args.kwargs["json"] == payload


@pytest.mark.parametrize("status,codigo", [(400, None), (401, None), (403, None), (409, "CPF_DUPLICADO"), (404, None), (429, None), (503, None)])
def test_patch_paciente_mapeia_erros_sem_expor_resposta(cliente, http, status, codigo):
    http.return_value = resposta({"codigo": codigo, "mensagem": "DADO_PESSOAL"}, status)

    with pytest.raises(ErroAcesso) as erro:
        cliente.atualizar_paciente("token-ficticio", 19, **dados())

    assert "DADO_PESSOAL" not in str(erro.value)
    if codigo == "CPF_DUPLICADO":
        assert str(erro.value) == "CPF já cadastrado."


def test_patch_paciente_rejeita_dados_invalidos_sem_rede(cliente, http):
    entrada = dados()
    entrada["cpf"] = "111.111.111-11"

    with pytest.raises(ErroAcesso):
        cliente.atualizar_paciente("token-ficticio", 19, **entrada)

    http.assert_not_called()


def test_patch_paciente_nao_confirma_resposta_de_outro_paciente(cliente, http):
    http.return_value = resposta({"paciente": {"id": 20, **dados()}})

    with pytest.raises(ErroAcesso):
        cliente.atualizar_paciente("token-ficticio", 19, **dados())
