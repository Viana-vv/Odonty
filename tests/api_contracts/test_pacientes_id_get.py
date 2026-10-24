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


@pytest.mark.parametrize("campos_vazios", [
    ("cpf",), ("celular",), ("email",), ("telefone",),
    ("cpf", "celular", "email"),
])
def test_get_paciente_abre_cadastro_antigo_com_campos_incompletos(cliente, http, campos_vazios):
    paciente = {**PACIENTE, **dict.fromkeys(campos_vazios, "")}
    http.return_value = resposta({"paciente": paciente})

    dados = cliente.obter_paciente("token-ficticio", 19)

    assert dados["id"] == 19
    assert dados["nome"] == paciente["nome"]
    assert all(dados[campo] == "" for campo in campos_vazios)


def test_get_cadastro_incompleto_nao_permite_salvar_sem_preencher(cliente, http):
    http.return_value = resposta({"paciente": {**PACIENTE, "cpf": "", "email": ""}})
    dados = cliente.obter_paciente("token-ficticio", 19)
    http.reset_mock()
    dados.pop("id")

    with pytest.raises(ErroAcesso) as erro:
        cliente.atualizar_paciente("token-ficticio", 19, **dados)

    assert erro.value.status == 400
    http.assert_not_called()


@pytest.mark.parametrize("campo,valor", [
    ("cpf", None), ("celular", []), ("email", {}),
    ("data_nascimento", "data-invalida"), ("data_nascimento", "1800-01-01"),
])
def test_get_paciente_rejeita_estrutura_incompativel(cliente, http, campo, valor):
    http.return_value = resposta({"paciente": {**PACIENTE, campo: valor}})

    with pytest.raises(ErroAcesso):
        cliente.obter_paciente("token-ficticio", 19)


def test_get_paciente_nao_chama_api_com_id_invalido(cliente, http):
    with pytest.raises(ValueError):
        cliente.obter_paciente("token-ficticio", 0)
    http.assert_not_called()
