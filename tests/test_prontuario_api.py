from unittest.mock import Mock

import pytest
import requests

from sorrisomais.api import ClienteXano, ErroAcesso
from sorrisomais.config import Configuracao


BASE = "https://exemplo.invalid/api:teste"


def resposta(payload, status=200):
    response = Mock(status_code=status)
    response.__enter__ = Mock(return_value=response)
    response.__exit__ = Mock(return_value=False)
    response.json.return_value = payload
    return response


@pytest.fixture
def cliente():
    return ClienteXano(Configuracao(BASE, timeout=3))


@pytest.fixture
def http(monkeypatch):
    mock = Mock()
    monkeypatch.setattr(requests, "request", mock)
    return mock


def agregado():
    return {
        "paciente": {"id": 8, "nome": "Paciente Fictício", "cpf": None},
        "prontuario": {"id": 12, "paciente_id": 8, "situacao": "ativo"},
        "anamnese": [],
        "historico_odontologico": [],
        "odontograma": [],
        "exame_clinico": [],
        "diagnosticos": [],
        "plano_tratamento": [],
        "procedimentos": [],
        "exames": [],
        "prescricoes": [],
        "evolucoes": [],
        "documentos": [],
    }


def secao(id=21, paciente_id=8, nome="anamnese"):
    return {
        "secao": {
            "id": id,
            "paciente_id": paciente_id,
            "prontuario_id": 12,
            "tipo": nome,
            "conteudo": {"alergias": "Nenhuma"},
            "versao": 1,
        }
    }


def test_listar_consulta_agregada_valida_colecoes_e_ids(cliente, http):
    http.return_value = resposta(agregado())

    resultado = cliente.listar_consulta_agregada("token-ficticio", 8)

    assert resultado["paciente"]["id"] == 8
    assert resultado["exames"] == []
    chamada = http.call_args
    assert chamada.args[:2] == ("GET", f"{BASE}/prontuarios/8")


def test_listar_consulta_agregada_rejeita_colecao_ausente(cliente, http):
    corpo = agregado()
    del corpo["diagnosticos"]
    http.return_value = resposta(corpo)

    with pytest.raises(ErroAcesso):
        cliente.listar_consulta_agregada("token-ficticio", 8)


def test_listar_consulta_agregada_rejeita_id_de_paciente_inconsistente(cliente, http):
    corpo = agregado()
    corpo["paciente"]["id"] = 9
    http.return_value = resposta(corpo)

    with pytest.raises(ErroAcesso):
        cliente.listar_consulta_agregada("token-ficticio", 8)


def test_criar_secao_valida_entrada_e_resposta(cliente, http):
    http.return_value = resposta(secao(), status=201)

    resultado = cliente.criar_secao_prontuario(
        "token-ficticio", 8, "anamnese", {"alergias": "Nenhuma"}, consulta_id=3,
    )

    assert resultado["id"] == 21
    payload = http.call_args.kwargs["json"]
    assert payload == {
        "tipo": "anamnese",
        "conteudo": '{"alergias": "Nenhuma"}',
        "consulta_id": 3,
        "liberado_paciente": False,
    }
    assert http.call_args.args[:2] == ("POST", f"{BASE}/prontuarios/8/secoes")


@pytest.mark.parametrize(
    "kwargs, mensagem",
    [
        ({"paciente_id": 0}, "Paciente"),
        ({"paciente_id": 8, "secao": "desconhecida"}, "seção"),
        ({"paciente_id": 8, "conteudo": {}}, "conteúdo"),
    ],
)
def test_criar_secao_rejeita_entrada_invalida_antes_da_rede(cliente, http, kwargs, mensagem):
    parametros = {
        "paciente_id": 8,
        "secao": "anamnese",
        "conteudo": {"alergias": "Nenhuma"},
    }
    parametros.update(kwargs)

    with pytest.raises(ErroAcesso, match=mensagem):
        cliente.criar_secao_prontuario("token-ficticio", **parametros)
    http.assert_not_called()


def test_retificar_secao_valida_justificativa_e_resposta(cliente, http):
    http.return_value = resposta(secao(id=22), status=201)

    resultado = cliente.retificar_secao_prontuario(
        "token-ficticio", 8, 21, {"alergias": "Penicilina"}, "Atualização fictícia",
    )

    assert resultado["id"] == 22
    assert http.call_args.args[:2] == (
        "POST", f"{BASE}/prontuarios/8/secoes/21/retificacao",
    )
    assert http.call_args.kwargs["json"]["justificativa"] == "Atualização fictícia"


def test_retificar_secao_rejeita_conteudo_invalido_antes_da_rede(cliente, http):
    with pytest.raises(ErroAcesso, match="conteúdo"):
        cliente.retificar_secao_prontuario("token-ficticio", 8, 21, [], "Motivo")
    http.assert_not_called()
