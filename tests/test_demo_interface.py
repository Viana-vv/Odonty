from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import Mock

import pytest
from streamlit.testing.v1 import AppTest

from sorrisomais.api import ClienteXano, ContaAcesso, Credencial


@pytest.fixture
def xano_demo(monkeypatch):
    monkeypatch.setenv("XANO_API_BASE_URL", "https://exemplo.invalid/api:teste")
    monkeypatch.setenv("SORRISOMAIS_MODO_DEMONSTRACAO", "1")
    validade = datetime.now(timezone.utc) + timedelta(hours=1)
    entrar = Mock(return_value=Credencial("token-ficticio", validade))
    identificar = Mock(return_value=ContaAcesso(1, "Conta Fictícia", ("administrador",), validade))
    sair = Mock(return_value=None)
    monkeypatch.setattr(ClienteXano, "entrar", entrar)
    monkeypatch.setattr(ClienteXano, "identificar", identificar)
    monkeypatch.setattr(ClienteXano, "sair", sair)
    return entrar, identificar, sair


def abrir_demo(api, perfil="administrador"):
    entrar, identificar, _ = api
    conta = identificar.return_value
    if perfil != "administrador":
        identificar.return_value = ContaAcesso(conta.id, conta.nome, (perfil,), conta.expira_em)
    app = AppTest.from_file(Path(__file__).resolve().parents[1] / "app.py", default_timeout=20).run()
    app.text_input(key="email").set_value("pessoa@example.com")
    app.text_input(key="senha").set_value("senha-ficticia")
    app.button(key="login-entrar").click().run()
    assert not app.exception
    entrar.assert_called_once()
    return app


def test_modo_demonstrativo_usa_login_xano_e_apresenta_aviso(xano_demo):
    app = abrir_demo(xano_demo)
    assert any("dados fictícios guardados somente nesta sessão" in info.value for info in app.info)
    assert "sorrisomais_demo_dados" in app.session_state
    assert xano_demo[1].call_count >= 1


def test_navegacao_abre_agenda_demo_sem_chamar_xano(xano_demo):
    app = abrir_demo(xano_demo)
    chamadas_identidade = xano_demo[1].call_count
    app.button(key="demo-nav-agenda").click().run()
    assert not app.exception
    assert any(item.value == "Agenda" for item in app.title)
    assert xano_demo[0].call_count == 1
    assert xano_demo[1].call_count == chamadas_identidade  # Conta de Acesso ainda dentro da janela de cache


def test_recepcao_nao_recebe_navegacao_de_prontuario(xano_demo):
    app = abrir_demo(xano_demo, "recepcionista")
    assert all(button.label != "Prontuários" for button in app.button)
    assert all("Evolução fictícia" not in item.value for item in app.markdown)


def test_login_permanece_no_xano_no_modo_demonstrativo(xano_demo):
    abrir_demo(xano_demo)
    assert xano_demo[0].call_args.args == ("pessoa@example.com", "senha-ficticia")
