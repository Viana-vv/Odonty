"""Verificação opt-in do fluxo visual com contas e dados fictícios no Xano."""

import os
import subprocess
import sys
import time
from pathlib import Path

import pytest
import requests
from playwright.sync_api import sync_playwright

from test_xano_real import Ambiente


pytestmark = pytest.mark.skipif(
    os.getenv("XANO_TESTAR_PACIENTE_NAVEGADOR") != "1",
    reason="Verificação de navegador exige autorização explícita.",
)


def test_navegacao_administrador_e_recepcionista_em_telas_responsivas():
    ambiente = Ambiente()
    contas = []
    processo = None
    raiz = Path(__file__).resolve().parents[1]
    porta = "8599"
    base_local = f"http://127.0.0.1:{porta}"
    capturas = raiz / "test-results" / "cadastro-paciente"
    capturas.mkdir(parents=True, exist_ok=True)
    variaveis = os.environ.copy()
    variaveis["XANO_API_BASE_URL"] = ambiente.base
    variaveis["XANO_CADASTRO_PACIENTE_HABILITADO"] = "1"

    try:
        for perfil in ("administrador", "recepcionista"):
            contas.append((perfil, ambiente.criar([perfil])))
        processo = subprocess.Popen(
            [sys.executable, "-B", "-m", "streamlit", "run", "app.py",
             "--server.headless", "true", "--server.address", "127.0.0.1",
             "--server.port", porta, "--browser.gatherUsageStats", "false"],
            cwd=raiz, env=variaveis, stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        limite = time.monotonic() + 45
        while time.monotonic() < limite:
            if processo.poll() is not None:
                pytest.fail("O servidor Streamlit encerrou antes de responder.")
            try:
                if requests.get(base_local, timeout=2).status_code == 200:
                    break
            except requests.RequestException:
                time.sleep(0.5)
        else:
            pytest.fail("O servidor Streamlit não ficou disponível no tempo esperado.")

        navegador = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
        if not navegador.exists():
            pytest.skip("Chrome não está instalado para a verificação de navegador.")
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True, executable_path=str(navegador))
            for perfil, conta in contas:
                pagina = browser.new_page(viewport={"width": 1440, "height": 1000})
                pagina.goto(base_local, wait_until="networkidle")
                pagina.get_by_label("E-mail").fill(conta["email"])
                pagina.get_by_label("Senha", exact=True).fill(conta["senha"])
                pagina.get_by_role("button", name="Entrar").click()
                pagina.get_by_role(
                    "button", name="Cadastrar paciente", exact=True
                ).wait_for(timeout=20000)
                pagina.get_by_role("button", name="Cadastrar paciente").click()
                pagina.get_by_role("heading", name="Cadastrar paciente").wait_for()

                for largura, altura, dispositivo in (
                    (1440, 1000, "computador"),
                    (768, 1024, "tablet"),
                    (390, 844, "celular"),
                ):
                    pagina.set_viewport_size({"width": largura, "height": altura})
                    for rotulo in ("Nome completo *", "Data de nascimento *", "Telefone *",
                                   "CPF *", "E-mail *", "Celular *"):
                        campo = (pagina.locator('[data-testid="stDateInput"]')
                                 if rotulo == "Data de nascimento *"
                                 else pagina.get_by_label(rotulo))
                        assert campo.is_visible(), (perfil, dispositivo, rotulo)
                    assert pagina.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
                    pagina.screenshot(path=str(capturas / f"{perfil}-{dispositivo}.png"), full_page=True)

                pagina.get_by_label("Nome completo *").focus()
                pagina.keyboard.press("Tab")
                assert pagina.evaluate("document.activeElement !== document.body")
                pagina.get_by_role("button", name="Voltar").click()
                pagina.get_by_role("button", name="Cadastrar paciente").wait_for()
                pagina.close()
            browser.close()
    finally:
        if processo and processo.poll() is None:
            processo.terminate()
            try:
                processo.wait(timeout=10)
            except subprocess.TimeoutExpired:
                processo.kill()
        for identificador in ambiente.criadas:
            ambiente.metadados("PUT", f"/table/{ambiente.contas}/content/{identificador}",
                                json={"situacao": "inativo"})
        ambiente.admin.close()
