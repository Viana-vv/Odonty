from pathlib import Path
import sys
from unittest.mock import Mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest

from sorrisomais.api import ErroAcesso
from sorrisomais.config import Configuracao
from sorrisomais.procedimentos_consulta import ClienteProcedimentosConsulta


class Resposta:
    def __init__(self, status_code, corpo):
        self.status_code = status_code
        self._corpo = corpo

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def json(self):
        return self._corpo


def cliente():
    return ClienteProcedimentosConsulta(Configuracao("https://exemplo.invalid/api:sorriso"))


def test_patch_realizacao_envia_rota_e_retorna_vinculo(monkeypatch):
    resposta = {"procedimento": {"id": 31, "situacao": "realizado", "realizado_em": "2026-10-24T10:00:00Z"}}
    chamada = Mock(return_value=Resposta(200, resposta))
    monkeypatch.setattr("sorrisomais.procedimentos_consulta.requests.request", chamada)

    item = cliente().marcar_procedimento_realizado("token-ficticio", 12, 31)

    assert item == resposta["procedimento"]
    args, kwargs = chamada.call_args
    assert args == ("PATCH", "https://exemplo.invalid/api:sorriso/consultas/12/procedimentos/31/realizacao")
    assert kwargs["headers"]["Authorization"] == "Bearer token-ficticio"
    assert "json" not in kwargs


def test_patch_realizacao_trata_conflito_e_resposta_invalida(monkeypatch):
    monkeypatch.setattr("sorrisomais.procedimentos_consulta.requests.request", Mock(return_value=Resposta(409, {})))
    with pytest.raises(ErroAcesso) as erro:
        cliente().marcar_procedimento_realizado("token-ficticio", 12, 31)
    assert erro.value.status == 409
    assert "mudou" in str(erro.value)

    monkeypatch.setattr("sorrisomais.procedimentos_consulta.requests.request", Mock(return_value=Resposta(200, {})))
    with pytest.raises(ErroAcesso):
        cliente().marcar_procedimento_realizado("token-ficticio", 12, 31)


def test_patch_realizacao_rejeita_identificadores_invalidos_sem_rede(monkeypatch):
    requisicao = Mock()
    monkeypatch.setattr("sorrisomais.procedimentos_consulta.requests.request", requisicao)
    with pytest.raises(ErroAcesso):
        cliente().marcar_procedimento_realizado("token-ficticio", 12, -1)
    requisicao.assert_not_called()
