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


def test_get_consulta_procedimentos_envia_token_e_devolve_lista(monkeypatch):
    chamada = Mock(return_value=Resposta(200, {"procedimentos": [{"id": 31, "situacao": "planejado"}]}))
    monkeypatch.setattr("sorrisomais.procedimentos_consulta.requests.request", chamada)

    itens = cliente().listar_procedimentos_consulta("token-ficticio", 12)

    assert itens == [{"id": 31, "situacao": "planejado"}]
    chamada.assert_called_once()
    args, kwargs = chamada.call_args
    assert args == ("GET", "https://exemplo.invalid/api:sorriso/consultas/12/procedimentos")
    assert kwargs["headers"]["Authorization"] == "Bearer token-ficticio"
    assert kwargs["allow_redirects"] is False


def test_get_consulta_procedimentos_trata_permissao_e_resposta_invalida(monkeypatch):
    monkeypatch.setattr("sorrisomais.procedimentos_consulta.requests.request", Mock(return_value=Resposta(403, {})))
    with pytest.raises(ErroAcesso) as erro:
        cliente().listar_procedimentos_consulta("token-ficticio", 12)
    assert erro.value.status == 403
    assert "permissão" in str(erro.value)

    monkeypatch.setattr("sorrisomais.procedimentos_consulta.requests.request", Mock(return_value=Resposta(200, {"procedimentos": None})))
    with pytest.raises(ErroAcesso):
        cliente().listar_procedimentos_consulta("token-ficticio", 12)


def test_get_consulta_procedimentos_rejeita_id_invalido_sem_rede(monkeypatch):
    requisicao = Mock()
    monkeypatch.setattr("sorrisomais.procedimentos_consulta.requests.request", requisicao)
    with pytest.raises(ErroAcesso):
        cliente().listar_procedimentos_consulta("token-ficticio", 0)
    requisicao.assert_not_called()
