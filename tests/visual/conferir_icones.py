"""Confere iconografia, semântica e controles reais com dados fictícios e rede externa bloqueada."""
from pathlib import Path
import os
import subprocess
import sys
import time
from urllib.request import urlopen

from playwright.sync_api import sync_playwright

RAIZ = Path(__file__).resolve().parents[2]
DESTINO = RAIZ / "test-results/icones-regen"
CASOS = [("controles", "administrador"), ("portal_login", "paciente"), ("portal", "paciente"),
         ("contas", "administrador"), ("procedimentos_consulta", "profissional")]
CASOS += [(f"demo_{area}", "administrador") for area in ("inicio", "agenda", "pacientes", "profissionais", "prontuarios", "procedimentos")]
CASOS.append(("carregando", "administrador"))
CASOS.append(("agenda", "recepcionista"))
if len(sys.argv) > 1:
    CASOS = [(tela, perfil) for tela, perfil in CASOS if tela in sys.argv[1:]]


def conferir_mascara(elemento, pseudo=None):
    estilo = elemento.evaluate('(e,p)=>{const s=getComputedStyle(e,p);return {mask:s.maskImage,cor:s.backgroundColor}}', pseudo)
    assert "data:image/svg+xml;base64," in estilo["mask"], estilo
    assert estilo["cor"] != "rgba(0, 0, 0, 0)", estilo


def main():
    DESTINO.mkdir(parents=True, exist_ok=True)
    ambiente = os.environ.copy()
    ambiente["XANO_API_BASE_URL"] = "https://exemplo.invalid/api:visual"
    processo = subprocess.Popen([sys.executable, "-B", "-m", "streamlit", "run", "tests/visual/app_referencias.py",
        "--server.headless=true", "--server.port=8526", "--browser.gatherUsageStats=false"], cwd=RAIZ, env=ambiente,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for _ in range(90):
            try:
                urlopen("http://127.0.0.1:8526", timeout=1).close()
                break
            except OSError:
                time.sleep(.5)
        with sync_playwright() as p:
            browser = p.chromium.launch()
            for tela, perfil in CASOS:
                page = browser.new_page(viewport={"width":1365,"height":900})
                page.route("**/*", lambda route: route.continue_() if route.request.url.startswith(("http://127.0.0.1:", "data:")) else route.abort())
                page.goto(f"http://127.0.0.1:8526/?tela={tela}&perfil={perfil}")
                page.locator('[data-testid="stButton"],[data-testid="stFormSubmitButton"]').first.wait_for()
                page.wait_for_timeout(600)
                assert page.locator('[data-testid="stException"]').count() == 0, page.locator("body").inner_text()
                for botao in page.locator('[data-testid="stButton"] button,[data-testid="stFormSubmitButton"] button').all():
                    if not botao.is_visible():
                        continue
                    conferir_mascara(botao, "::before")
                    assert botao.get_attribute("aria-label") or botao.inner_text().strip()
                if tela == "carregando":
                    carregamento = page.locator('[data-testid="stSpinnerIcon"]')
                    carregamento.wait_for()
                    conferir_mascara(carregamento)
                if tela == "agenda":
                    opcoes = page.locator('[data-testid="stPopoverButton"]')
                    conferir_mascara(opcoes, "::before")
                    opcoes.click()
                    seguinte = page.get_by_role("button", name="Dia seguinte", exact=True)
                    conferir_mascara(seguinte, "::before")
                    seguinte.click()
                if tela == "controles":
                    senha = page.get_by_label("Senha de teste", exact=True)
                    olho = page.get_by_role("button", name="Show password")
                    conferir_mascara(olho.locator('[data-testid="stIconMaterial"]'))
                    olho.click()
                    assert senha.get_attribute("type") == "text"
                    conferir_mascara(page.get_by_role("button", name="Hide password").locator('[data-testid="stIconMaterial"]'))
                    seletor = page.locator('[data-testid="stSelectbox"] button')
                    conferir_mascara(seletor.locator("svg"))
                    seletor.click()
                    page.get_by_role("option", name="Segunda", exact=True).click()
                    assert page.get_by_role("combobox").input_value() == "Segunda"
                    conferir_mascara(page.locator('[data-testid="stCheckbox"] svg'))
                    page.locator('[data-testid="stCheckbox"] label').click()
                    assert not page.get_by_role("checkbox").is_checked()
                    conferir_mascara(page.locator('[data-testid="stNumberInputStepUp"] svg'))
                    page.get_by_role("button", name="Increment", exact=True).click()
                    assert page.get_by_label("Quantidade de teste", exact=True).input_value() == "2"
                    campo_data = page.locator('[data-testid="stDateInputField"]')
                    campo_data.locator('[role="spinbutton"]').first.press("Alt+ArrowDown")
                    calendario = page.locator('[data-testid="stDateInputCalendar"]')
                    calendario.wait_for()
                    conferir_mascara(calendario.locator('button[slot="previous"] svg'))
                    conferir_mascara(calendario.locator('button[slot="next"] svg'))
                    calendario.locator('button[slot="next"]').click()
                    calendario.screenshot(path=str(DESTINO / "calendario.png"))
                    page.keyboard.press("Escape")
                    detalhes = page.locator('[data-testid="stExpander"] summary')
                    conferir_mascara(detalhes.locator('[data-testid="stIconMaterial"]'))
                    detalhes.click()
                    assert page.get_by_text("Conteúdo de teste", exact=True).is_visible()
                    assert page.get_by_role("button", name="Ação indisponível").is_disabled()
                    acao = page.get_by_role("button", name="Ação de teste", exact=True)
                    acao.focus()
                    page.keyboard.press("Enter")
                for largura in (1365,390):
                    page.set_viewport_size({"width":largura,"height":900 if largura==1365 else 844})
                    page.wait_for_timeout(150)
                    assert page.evaluate("document.documentElement.scrollWidth<=innerWidth"), tela
                    assert page.locator('[data-testid="stException"]').count() == 0
                    page.screenshot(path=str(DESTINO / f"{tela}-{perfil}-{largura}.png"),full_page=True)
                page.close()
                print(f"Ícones conferidos: {tela}/{perfil}", flush=True)
            browser.close()
    finally:
        processo.terminate()
        processo.wait(timeout=10)


if __name__ == "__main__":
    main()
