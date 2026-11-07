from pathlib import Path
from unittest.mock import Mock

from streamlit.testing.v1 import AppTest

from sorrisomais.api import ClienteXano


def test_tela_otp_exibe_seis_campos_e_mantem_codigo_unico(monkeypatch):
    monkeypatch.setenv("XANO_API_BASE_URL", "https://exemplo.invalid/api:teste")
    validar = Mock()
    monkeypatch.setattr(ClienteXano, "validar_otp", validar)
    app = AppTest.from_file(Path(__file__).resolve().parents[1] / "app.py", default_timeout=20)
    app.session_state["recuperacao_etapa"] = "otp"
    app.session_state["recuperacao_operacao"] = "op-ficticia"
    app.run()

    assert not app.exception
    campos = [campo for campo in app.text_input if campo.key.startswith("recuperacao_otp_")]
    assert len(campos) == 6
    for indice, campo in enumerate(campos, start=1):
        campo.set_value(str(indice))
    app.run()

    app.button[0].click().run()
    assert not app.exception
    validar.assert_called_once_with("op-ficticia", "123456")


def test_otp_move_foco_ao_digitar():
    codigo = (Path(__file__).resolve().parents[1] / "app.py").read_text(encoding="utf-8")
    assert "window.setTimeout(() => campos[indice + 1].focus(), 0)" in codigo
