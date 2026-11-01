"""Confere todas as composições existentes com dados fictícios e sem rede."""
from pathlib import Path
import os
import subprocess
import sys
import time
from urllib.request import urlopen
from base64 import b64encode
from playwright.sync_api import sync_playwright

RAIZ = Path(__file__).resolve().parents[2]
DESTINO = RAIZ / "test-results/reconstrucao-frontend"
TELAS = [("login", "administrador"), ("inicio", "administrador"),
         ("inicio", "recepcionista"), ("inicio", "profissional"),
         ("agenda", "recepcionista"), ("vazio", "recepcionista"),
         ("erro", "recepcionista"), ("pacientes", "administrador"),
         ("profissionais", "administrador"), ("procedimentos", "administrador"),
         ("prontuarios", "profissional"), ("paciente", "administrador"),
         ("cadastro", "administrador"), ("nova_consulta", "administrador"),
         ("evolucao", "profissional"), ("exames", "profissional"),
         ("reagendar_consulta", "administrador"), ("edicao", "administrador")]

if len(sys.argv) > 1:
    TELAS = [(tela, perfil) for tela, perfil in TELAS if tela in sys.argv[1:]]


def main():
    DESTINO.mkdir(parents=True, exist_ok=True)
    ambiente = os.environ.copy()
    ambiente["XANO_API_BASE_URL"] = "https://exemplo.invalid/api:visual"
    processo = subprocess.Popen([sys.executable, "-B", "-m", "streamlit", "run",
        "tests/visual/app_referencias.py", "--server.headless=true", "--server.port=8524",
        "--browser.gatherUsageStats=false"], cwd=RAIZ, env=ambiente,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    falhas = []
    try:
        for _ in range(90):
            try:
                urlopen("http://127.0.0.1:8524", timeout=1).close()
                break
            except OSError:
                time.sleep(.5)
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            for tela, perfil in TELAS:
                page = browser.new_page(viewport={"width":1365,"height":900})
                page.goto(f"http://127.0.0.1:8524/?tela={tela}&perfil={perfil}")
                page.locator(".st-key-entrada" if tela == "login" else ".st-key-menu-equipe").wait_for()
                page.wait_for_timeout(1500)
                if tela == "evolucao":
                    page.get_by_label("Evolução e observações").wait_for()
                if tela == "edicao":
                    page.get_by_role("button", name="Editar", exact=True).first.click()
                    page.get_by_role("dialog").wait_for()
                page.wait_for_function("Array.from(document.images).every(i=>i.complete && i.naturalWidth>0)")
                marca = page.locator(".assinatura-sorriso>img").first
                imagem_marca = b64encode((RAIZ / "assets/mascotes-tratados/04-profissionais.png").read_bytes()).decode("ascii")
                assert marca.get_attribute("src") == "data:image/png;base64," + imagem_marca
                if tela not in {"inicio", "login"}:
                    assert page.locator(".banner-contextual").count() == 0, tela + ": banner indevido"
                if tela == "inicio":
                    prefixo = {"administrador":"metrica-admin-", "recepcionista":"metrica-xano-", "profissional":"painel-profissional-metrica-"}[perfil]
                    quantidade = 4
                    assert page.locator(f'[class*="st-key-{prefixo}"]').count() == quantidade
                    assert page.locator(".icone-metrica").count() == quantidade
                if tela == "agenda":
                    assert page.locator(".agenda-tabela thead th").count() == 5
                    assert page.locator(".agenda-tabela tbody tr").count() == 5
                for largura in (1365,390):
                    page.set_viewport_size({"width":largura,"height":900 if largura==1365 else 844})
                    page.wait_for_timeout(200)
                    nome = f"{tela}-{perfil}-{largura}"
                    if page.locator('[data-testid="stException"]').count():
                        falhas.append(nome+": "+page.locator('[data-testid="stException"]').inner_text())
                    if not page.evaluate("document.documentElement.scrollWidth <= innerWidth"):
                        falhas.append(nome+": largura excedida")
                    page.screenshot(path=str(DESTINO / f"{nome}.png"),full_page=True)
                    conteudo = page.locator(".st-key-conteudo-equipe")
                    if conteudo.count():
                        conteudo.evaluate("e=>e.scrollIntoView({block:'start'})")
                        page.screenshot(path=str(DESTINO / f"{nome}-conteudo.png"))
                    if page.get_by_role("dialog").count():
                        page.get_by_role("dialog").screenshot(path=str(DESTINO / f"{nome}-modal.png"))
                    if largura == 1365 and tela in {"inicio", "pacientes"}:
                        conferir_rolagens(page, nome)
                if tela == "agenda":
                    page.get_by_text("Gerenciar consultas e horários", exact=True).click()
                    page.get_by_text("Gerenciar consulta", exact=True).first.click()
                    page.get_by_label("Alterar situação").first.wait_for()
                if tela == "evolucao":
                    page.get_by_role("button", name="Salvar no prontuário", exact=True).click()
                    page.get_by_text("Informe a evolução clínica antes de salvar.", exact=True).wait_for()
                if tela in {"edicao", "evolucao", "nova_consulta", "paciente"}:
                    page.get_by_role("button", name="Cancelar", exact=True).click()
                    if tela == "edicao":
                        page.get_by_role("dialog").wait_for(state="hidden")
                    elif tela == "evolucao":
                        page.locator(".st-key-modal-nova-evolucao").wait_for(state="hidden")
                    elif tela == "paciente":
                        page.locator(".st-key-modal-paciente").wait_for(state="hidden")
                    else:
                        page.locator(".st-key-formulario-nova-consulta").wait_for(state="hidden")
                assert page.locator('[data-testid="stException"]').count() == 0
                print(f"Conferido: {tela}/{perfil}",flush=True)
                page.close()
            browser.close()
    finally:
        processo.terminate()
        processo.wait(timeout=10)
    (DESTINO / "resultado.txt").write_text("\n".join(falhas) or f"{len(TELAS)} composições em 2 resoluções: sem exceções, imagens carregadas e largura válida.", encoding="utf-8")
    assert not falhas, "\n".join(falhas)


def conferir_rolagens(page, nome):
    """Exercita rolagens naturais em janela baixa, sem inflar o DOM."""
    page.set_viewport_size({"width":1365,"height":300})
    menu = page.locator(".st-key-menu-equipe")
    conteudo = page.locator(".st-key-conteudo-equipe")
    principal = page.get_by_test_id("stMain")
    assert menu.evaluate("e=>getComputedStyle(e).position") == "fixed"
    assert menu.evaluate("e=>e.scrollHeight > e.clientHeight"), "Menu deve ter rolagem própria"
    assert conteudo.bounding_box()["x"] >= menu.bounding_box()["width"] - 1
    y_menu = menu.bounding_box()["y"]
    y_conteudo = conteudo.bounding_box()["y"]
    principal.evaluate("e=>e.scrollTo(0,400)")
    page.wait_for_timeout(150)
    assert principal.evaluate("e=>e.scrollTop") > 0
    assert conteudo.bounding_box()["y"] < y_conteudo
    assert abs(menu.bounding_box()["y"] - y_menu) < 1
    rolagem_conteudo = principal.evaluate("e=>e.scrollTop")
    menu.evaluate("e=>e.scrollTo(0,e.scrollHeight)")
    assert menu.evaluate("e=>e.scrollTop") > 0
    assert principal.evaluate("e=>e.scrollTop") == rolagem_conteudo
    page.mouse.move(110,300)
    page.mouse.wheel(0,600)
    page.wait_for_timeout(150)
    assert principal.evaluate("e=>e.scrollTop") == rolagem_conteudo, "Rolagem do menu propagou ao conteúdo"
    page.screenshot(path=str(DESTINO / f"{nome}-rolagens-independentes.png"))
    menu.evaluate("e=>e.scrollTop=0")
    principal.evaluate("e=>e.scrollTop=0")


if __name__ == "__main__":
    main()
