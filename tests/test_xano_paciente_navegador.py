"""Verificação opt-in do fluxo visual com contas e dados fictícios no Xano."""

import os
import secrets
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import pytest
import requests
from playwright.sync_api import sync_playwright

from test_xano_real import Ambiente
from test_xano_pacientes_real import cpf_ficticio


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


def test_recepcionista_completa_cadastro_antigo_no_xano_real():
    ambiente = Ambiente()
    processo = None
    paciente_id = None
    tabela_pacientes = None
    raiz = Path(__file__).resolve().parents[1]
    base_local = "http://127.0.0.1:8598"
    capturas = Path(tempfile.gettempdir()) / "odonty-edicao-xano-real"
    capturas.mkdir(exist_ok=True)
    nome = "Paciente Fictício Legado " + secrets.token_hex(5)
    email = "legado." + secrets.token_hex(6) + "@example.invalid"
    try:
        conta = ambiente.criar(["recepcionista"])
        tabela_pacientes = next(t["id"] for t in ambiente.listar("/table")
                               if t["name"] == "paciente")
        paciente = ambiente.metadados("POST", f"/table/{tabela_pacientes}/content", json={
            "nome": nome, "data_nascimento": "2000-02-29", "telefone": "11900000000",
            "cpf": None, "celular": None, "email": None, "situacao": "ativo",
        })
        paciente_id = paciente["id"]
        env = os.environ.copy()
        env.update({
            "PYTHONPATH": str(raiz / "tests" / "fixtures"),
            "ODONTY_XANO_REAL_TEST": "1", "ODONTY_AGENDA_FICTICIA": "0",
            "SORRISOMAIS_MODO_DEMONSTRACAO": "0",
        })
        time.sleep(3.1)
        processo = subprocess.Popen(
            [sys.executable, "-B", "-m", "streamlit", "run", "app.py",
             "--server.headless=true", "--server.address=127.0.0.1",
             "--server.port=8598", "--browser.gatherUsageStats=false"],
            cwd=raiz, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        limite = time.monotonic() + 45
        while time.monotonic() < limite:
            if processo.poll() is not None:
                pytest.fail("O Streamlit encerrou antes de iniciar o teste real.")
            try:
                if requests.get(base_local, timeout=2).status_code == 200:
                    break
            except requests.RequestException:
                time.sleep(0.5)
        else:
            pytest.fail("O Streamlit não iniciou no prazo do teste real.")

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            pagina = browser.new_page(viewport={"width": 1365, "height": 900})
            pagina.set_default_timeout(60000)
            pagina.goto(base_local, wait_until="domcontentloaded")
            pagina.get_by_label("E-mail").fill(conta["email"])
            pagina.get_by_label("Senha", exact=True).fill(conta["senha"])
            pagina.get_by_role("button", name="Entrar", exact=True).click()
            pagina.get_by_role("button", name="Pacientes", exact=True).click()
            pagina.get_by_placeholder("Buscar por nome...").fill(nome)
            pagina.get_by_placeholder("Buscar por nome...").press("Enter")
            pagina.get_by_text("1 pacientes", exact=True).wait_for()
            pagina.get_by_role("button", name="Editar", exact=True).click()
            dialogo = pagina.get_by_role("dialog")
            dialogo.wait_for()
            for campo in ("CPF *", "Celular *", "E-mail *"):
                assert dialogo.get_by_label(campo, exact=True).input_value() == ""
            pagina.screenshot(path=str(capturas / "cadastro-incompleto.png"))
            dialogo.get_by_label("Nome completo *").fill(nome + " Atualizado")
            dialogo.get_by_label("CPF *", exact=True).fill(cpf_ficticio())
            dialogo.get_by_label("Celular *", exact=True).fill("11911112222")
            dialogo.get_by_label("E-mail *", exact=True).fill(email)
            dialogo.get_by_role("button", name="Salvar alterações", exact=True).click()
            dialogo.wait_for(state="hidden")
            pagina.get_by_text("Os dados cadastrais do Paciente foram atualizados.", exact=True).wait_for()
            pagina.get_by_text(nome + " Atualizado", exact=True).wait_for()
            pagina.get_by_role("button", name="Editar", exact=True).click()
            dialogo.wait_for()
            assert dialogo.get_by_label("E-mail *", exact=True).input_value() == email
            assert dialogo.get_by_label("Nome completo *").input_value() == nome + " Atualizado"
            pagina.screenshot(path=str(capturas / "cadastro-reaberto.png"))
            dialogo.get_by_role("button", name="Cancelar", exact=True).click()
            dialogo.wait_for(state="hidden")
            pagina.get_by_role("button", name="Sair", exact=True).click()
            pagina.get_by_role("button", name="Entrar", exact=True).wait_for()
            browser.close()
    finally:
        if processo and processo.poll() is None:
            processo.terminate()
            try:
                processo.wait(timeout=10)
            except subprocess.TimeoutExpired:
                processo.kill()
                processo.wait(timeout=5)
        time.sleep(3.1)
        if paciente_id is not None:
            inativado = ambiente.metadados("PUT", f"/table/{tabela_pacientes}/content/{paciente_id}",
                                           json={"situacao": "inativo"})
            assert inativado["situacao"] == "inativo"
        for identificador in ambiente.criadas:
            inativada = ambiente.metadados("PUT", f"/table/{ambiente.contas}/content/{identificador}",
                                          json={"situacao": "inativo"})
            assert inativada["situacao"] == "inativo"
        ambiente.admin.close()
