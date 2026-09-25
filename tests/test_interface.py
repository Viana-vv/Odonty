"""Verifica a interface com respostas simuladas, sem chamadas externas."""
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from sorrisomais.api import ClienteXano, ContaAcesso, Credencial, ErroAcesso
from sorrisomais import sessao


@pytest.fixture
def cliente_simulado(monkeypatch):
    monkeypatch.setenv("XANO_API_BASE_URL", "https://exemplo.invalid/api:teste")
    prazo = datetime.now(timezone.utc) + timedelta(hours=1)
    entrar = Mock(return_value=Credencial("token-simulado", prazo))
    identificar = Mock(return_value=ContaAcesso(1, "Pessoa Ficticia", ("profissional",), prazo))
    sair = Mock()
    monkeypatch.setattr(ClienteXano, "entrar", entrar)
    monkeypatch.setattr(ClienteXano, "identificar", identificar)
    monkeypatch.setattr(ClienteXano, "sair", sair)
    return entrar, identificar, sair


def abrir():
    app = AppTest.from_file(Path(__file__).resolve().parents[1] / "app.py", default_timeout=20).run()
    assert not app.exception
    return app


def enviar(app):
    app.text_input[0].set_value("teste@example.com")
    app.text_input[1].set_value("senha-ficticia")
    app.button[0].click().run()
    assert not app.exception


def test_configuracao_ausente_desabilita_formulario(monkeypatch):
    monkeypatch.delenv("XANO_API_BASE_URL", raising=False)
    app = abrir()
    assert app.button[0].disabled
    assert all(campo.disabled for campo in app.text_input)


def test_login_logout_e_senha_removida(cliente_simulado):
    entrar, identificar, sair = cliente_simulado
    app = abrir()
    enviar(app)
    assert any(texto.value == "Pessoa Ficticia" for texto in app.text)
    assert any(texto.value == "Dentista" for texto in app.text)
    assert app.session_state["senha"] == ""
    assert not app.session_state["processando"]
    entrar.assert_called_once()
    assert identificar.call_count >= 1
    app.button[0].click().run()
    assert not app.exception
    sair.assert_called_once_with("token-simulado")
    assert len(app.text_input) == 2
    assert sessao.CHAVE not in app.session_state


@pytest.mark.parametrize("status", [401, 403, 429, 503])
def test_erro_reabilita_formulario(cliente_simulado, status):
    entrar, _, _ = cliente_simulado
    entrar.side_effect = ErroAcesso("Falha simulada segura.", status)
    app = abrir()
    enviar(app)
    assert app.error[0].value == "Falha simulada segura."
    assert not app.button[0].disabled
    assert app.session_state["senha"] == ""
    assert not app.session_state["processando"]
    assert sessao.CHAVE not in app.session_state


def test_falha_revalidacao_retira_conteudo(cliente_simulado):
    _, identificar, _ = cliente_simulado
    app = abrir()
    enviar(app)
    identificar.side_effect = ErroAcesso("Servico indisponivel.", 503)
    app.run()
    assert not app.exception
    assert len(app.text_input) == 2
    assert not any(texto.value == "Pessoa Ficticia" for texto in app.text)
    assert sessao.CHAVE not in app.session_state


def test_sessao_nova_nao_recupera_login(cliente_simulado):
    app = abrir()
    enviar(app)
    outra = abrir()
    assert len(outra.text_input) == 2
    assert sessao.CHAVE not in outra.session_state
