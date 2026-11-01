"""Captura login, painel, Agenda e Pacientes com API fictícia e verifica imagens."""
import os
from pathlib import Path
import subprocess
import sys
import time
from urllib.request import urlopen

from playwright.sync_api import sync_playwright

RAIZ = Path(__file__).resolve().parents[2]
DESTINO = RAIZ / "test-results" / "mascotes"


def main():
    DESTINO.mkdir(parents=True, exist_ok=True)
    ambiente = os.environ.copy()
    ambiente.update(XANO_API_BASE_URL="https://exemplo.invalid/api:agenda-ficticia",
                    SORRISOMAIS_MODO_DEMONSTRACAO="0", ODONTY_AGENDA_FICTICIA="1",
                    ODONTY_AGENDA_PERFIL="recepcionista",
                    PYTHONPATH=str(RAIZ / "tests" / "fixtures"))
    processo = subprocess.Popen([sys.executable, "-B", "-m", "streamlit", "run", "app.py",
                                 "--server.headless=true", "--server.port=8523",
                                 "--browser.gatherUsageStats=false"], cwd=RAIZ, env=ambiente,
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for _ in range(90):
            try:
                urlopen("http://127.0.0.1:8523", timeout=1).close()
                break
            except OSError:
                time.sleep(.5)
        with sync_playwright() as p:
            navegador = p.chromium.launch(headless=True)
            pagina = navegador.new_page(viewport={"width": 1365, "height": 900})
            pagina.goto("http://127.0.0.1:8523")
            pagina.get_by_label("E-mail").wait_for()
            capturar(pagina, "login")
            pagina.get_by_label("E-mail").fill("recepcao.ficticia@example.invalid")
            pagina.get_by_label("Senha").fill("senha-local-ficticia")
            pagina.get_by_role("button", name="Entrar", exact=True).click()
            pagina.locator(".banner-contextual").wait_for()
            capturar(pagina, "painel")
            for nome in ("Agenda", "Pacientes"):
                pagina.get_by_role("button", name=nome, exact=True).click()
                pagina.get_by_role("heading", name=nome, exact=True).wait_for()
                assert pagina.locator(".banner-contextual").count() == 0
                capturar(pagina, nome.lower())
            navegador.close()
    finally:
        processo.terminate()
        processo.wait(timeout=10)
    print(f"Capturas e verificações concluídas: {DESTINO}")


def capturar(pagina, nome):
    for largura, altura in ((1365, 900), (390, 844)):
        pagina.set_viewport_size({"width": largura, "height": altura})
        pagina.wait_for_timeout(600)
        pagina.wait_for_function("Array.from(document.images).every(i => i.complete && i.naturalWidth > 0)")
        assert pagina.locator('[data-testid="stException"]').count() == 0
        assert pagina.evaluate("document.documentElement.scrollWidth <= innerWidth")
        for banner in pagina.locator(".banner-contextual").all():
            texto = banner.locator(".banner-contextual-conteudo").bounding_box()
            arte = banner.locator(".banner-contextual-arte").bounding_box()
            assert texto["y"] + texto["height"] <= arte["y"] + 2 or texto["x"] + texto["width"] <= arte["x"] + 2
        pagina.screenshot(path=str(DESTINO / f"{nome}-{largura}.png"), full_page=True)
        if pagina.locator(".banner-contextual").count():
            pagina.locator(".banner-contextual").first.screenshot(path=str(DESTINO / f"{nome}-banner-{largura}.png"))
    pagina.set_viewport_size({"width": 1365, "height": 900})


if __name__ == "__main__":
    main()
