from pathlib import Path
import os
import socket
import subprocess
import sys
import time
from urllib.request import urlopen
from unittest.mock import Mock

import pytest
from playwright.sync_api import expect, sync_playwright
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


@pytest.fixture(scope="module")
def app_otp_no_navegador(tmp_path_factory):
    raiz = Path(__file__).resolve().parents[1]
    entrada = tmp_path_factory.mktemp("otp-navegador") / "app_otp_ficticio.py"
    entrada.write_text(
        "import runpy\n"
        "from unittest.mock import patch\n"
        "import streamlit as st\n"
        "from sorrisomais.api import ClienteXano\n"
        "st.session_state.setdefault('recuperacao_etapa', 'otp')\n"
        "st.session_state.setdefault('recuperacao_operacao', 'op-ficticia')\n"
        "def validar(self, operacao, otp):\n"
        "    st.session_state['otp_enviado_teste'] = otp\n"
        "if 'otp_enviado_teste' in st.session_state:\n"
        "    st.caption('OTP recebido pelo cliente: ' + st.session_state['otp_enviado_teste'])\n"
        "with patch.object(ClienteXano, 'validar_otp', validar), "
        "patch('requests.request', side_effect=AssertionError('Rede bloqueada no teste OTP')):\n"
        f"    runpy.run_path({str(raiz / 'app.py')!r}, run_name='__main__')\n"
        ,
        encoding="utf-8",
    )
    with socket.socket() as reserva:
        reserva.bind(("127.0.0.1", 0))
        porta = reserva.getsockname()[1]
    ambiente = os.environ.copy()
    ambiente.update(
        XANO_API_BASE_URL="https://exemplo.invalid/api:otp-ficticio",
        PYTHONPATH=str(raiz),
        PYTHONDONTWRITEBYTECODE="1",
    )
    processo = subprocess.Popen(
        [sys.executable, "-B", "-m", "streamlit", "run", str(entrada),
         "--server.headless=true", f"--server.port={porta}",
         "--browser.gatherUsageStats=false"],
        cwd=raiz, env=ambiente, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    url = f"http://127.0.0.1:{porta}"
    try:
        for _ in range(60):
            try:
                with urlopen(url + "/_stcore/health", timeout=1):
                    break
            except OSError:
                if processo.poll() is not None:
                    pytest.fail("O Streamlit de teste encerrou antes de iniciar.")
                time.sleep(0.2)
        else:
            pytest.fail("O Streamlit de teste não iniciou.")
        yield url
    finally:
        processo.terminate()
        processo.wait(timeout=10)


@pytest.mark.parametrize("largura", [1365, 390])
def test_otp_move_foco_ao_digitar(app_otp_no_navegador, largura):
    with sync_playwright() as playwright:
        navegador = playwright.chromium.launch(headless=True)
        try:
            contexto = navegador.new_context(
                viewport={"width": largura, "height": 900},
                permissions=["clipboard-read", "clipboard-write"],
            )
            pagina = contexto.new_page()
            pagina.goto(app_otp_no_navegador)
            campos = pagina.locator('.st-key-otp-campos input')
            expect(campos).to_have_count(6)
            campos.nth(0).click()
            pagina.keyboard.type("0")
            expect(campos.nth(1)).to_be_focused(timeout=2000)
            pagina.keyboard.type("12304", delay=40)
            assert campos.evaluate_all("es => es.map(e => e.value).join('')") == "012304"
            expect(campos.nth(5)).to_be_focused()
            pagina.keyboard.press("Backspace")
            expect(campos.nth(5)).to_have_value("")
            pagina.keyboard.press("Backspace")
            expect(campos.nth(4)).to_be_focused()
            pagina.keyboard.type("9")
            expect(campos.nth(5)).to_be_focused()
            campos.nth(0).click()
            pagina.keyboard.type("a")
            expect(campos.nth(0)).to_have_value("0")
            expect(campos.nth(0)).to_be_focused()
            pagina.evaluate("navigator.clipboard.writeText('012304')")
            pagina.keyboard.press("Control+V")
            expect(campos.nth(5)).to_have_value("4")
            assert campos.evaluate_all("es => es.map(e => e.value).join('')") == "012304"
            assert pagina.evaluate("document.documentElement.scrollWidth <= innerWidth")
            pagina.get_by_role("button", name="Validar código", exact=True).click()
            expect(pagina.get_by_role("heading", name="Crie uma nova senha")).to_be_visible()
            expect(pagina.get_by_text("OTP recebido pelo cliente: 012304", exact=True)).to_be_visible()
            expect(pagina.locator('[data-testid="stException"]')).to_have_count(0)
        finally:
            navegador.close()
