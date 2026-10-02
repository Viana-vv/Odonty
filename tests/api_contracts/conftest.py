from datetime import datetime, timedelta, timezone
from unittest.mock import Mock

import pytest
import requests

from sorrisomais.api import ClienteXano
from sorrisomais.config import Configuracao

BASE = "https://exemplo.invalid/api:teste"
FUTURO = (datetime.now(timezone.utc) + timedelta(hours=1)).replace(microsecond=0)


def resposta(payload=None, status=200):
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

