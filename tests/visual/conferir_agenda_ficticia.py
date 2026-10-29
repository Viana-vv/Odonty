"""Abre a interface real do Streamlit com Xano inteiramente simulado e salva capturas."""
import os
from datetime import date, timedelta
from pathlib import Path
import subprocess
import sys
import tempfile
import time
from urllib.error import URLError
from urllib.request import urlopen

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[2]
PORT = 8517
URL = f"http://127.0.0.1:{PORT}"


def esperar_app():
    limite = time.monotonic() + 45
    while time.monotonic() < limite:
        try:
            with urlopen(URL, timeout=1) as resposta:
                if resposta.status == 200:
                    return
        except (URLError, TimeoutError):
            time.sleep(0.4)
    raise RuntimeError("Streamlit não iniciou no prazo esperado.")


def main():
    env = os.environ.copy()
    env.update({
        "XANO_API_BASE_URL": "https://exemplo.invalid/api:agenda-ficticia",
        "SORRISOMAIS_MODO_DEMONSTRACAO": "0",
        "ODONTY_AGENDA_FICTICIA": "1",
        "ODONTY_AGENDA_FICTICIA_DATA": date.today().isoformat(),
        "ODONTY_AGENDA_PERFIL": "recepcionista",
        "PYTHONPATH": str(ROOT / "tests" / "fixtures"),
    })
    destino = Path(tempfile.gettempdir()) / "odonty-agenda-ficticia"
    destino.mkdir(exist_ok=True)
    processo = subprocess.Popen([
        sys.executable, "-B", "-m", "streamlit", "run", "app.py",
        "--server.headless=true", f"--server.port={PORT}",
        "--browser.gatherUsageStats=false",
    ], cwd=ROOT, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        esperar_app()
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1365, "height": 900}, device_scale_factor=1)
            page.set_default_timeout(20000)
            page.goto(URL, wait_until="domcontentloaded")
            page.get_by_label("E-mail").fill("recepcao.ficticia@example.invalid")
            page.get_by_label("Senha").fill("senha-local-ficticia")
            page.get_by_role("button", name="Entrar").click()
            page.get_by_role("button", name="Agenda", exact=True).click()
            page.get_by_text("Paciente Fictícia Aurora", exact=False).wait_for()
            page.wait_for_timeout(2000)
            page.screenshot(path=destino / "agenda-desktop.png", full_page=True)
            menu = page.locator(".st-key-menu-equipe")
            coluna_menu = page.get_by_test_id("stColumn").filter(has=menu)
            assert coluna_menu.evaluate("element => getComputedStyle(element).position") == "sticky"
            page.locator(".st-key-conteudo-equipe").evaluate(
                "element => element.style.minHeight = '1800px'"
            )
            area_rolagem = page.get_by_test_id("stMain")
            conteudo_pagina = page.locator(".st-key-conteudo-equipe")
            menu_antes = menu.bounding_box()["y"]
            conteudo_antes = conteudo_pagina.bounding_box()["y"]
            area_rolagem.evaluate("element => element.scrollTo(0, 600)")
            page.wait_for_function(
                "document.querySelector('[data-testid=stMain]').scrollTop >= 500"
            )
            page.wait_for_timeout(250)
            assert conteudo_antes - conteudo_pagina.bounding_box()["y"] >= 500
            menu_depois = menu.bounding_box()["y"]
            page.screenshot(path=destino / "agenda-desktop-rolagem.png")
            assert abs(menu_depois - menu_antes) <= 2, (
                f"O menu acompanhou a rolagem: {menu_antes} -> {menu_depois}."
            )
            area_rolagem.evaluate("element => element.scrollTo(0, 0)")
            conteudo = page.locator("body").inner_text()
            assert "Dra. Exemplo Sorriso" in conteudo
            assert "Profilaxia fictícia" in conteudo
            assert "FICTICIO-NAO-EXIBIR" not in conteudo
            assert "CPF" not in conteudo
            assert "Aqui está um resumo da clínica hoje." not in conteudo, conteudo
            largura = page.evaluate("({viewport: document.documentElement.clientWidth, pagina: document.documentElement.scrollWidth})")
            assert largura["pagina"] <= largura["viewport"], f"Rolagem horizontal no desktop: {largura}"

            page.get_by_role("button", name="Novo horário").click()
            page.get_by_role("group", name="Data do horário").wait_for()
            assert page.get_by_label("Profissional").is_visible()
            page.get_by_role("group", name="Horário inicial").wait_for()
            page.get_by_role("group", name="Horário final").wait_for()
            page.set_viewport_size({"width": 390, "height": 844})
            assert coluna_menu.evaluate("element => getComputedStyle(element).position") == "static"
            largura = page.evaluate("({viewport: document.documentElement.clientWidth, pagina: document.documentElement.scrollWidth})")
            assert largura["pagina"] <= largura["viewport"], f"Rolagem horizontal no formulário de horário: {largura}"
            page.screenshot(path=destino / "novo-horario-celular.png", full_page=True)
            page.set_viewport_size({"width": 1365, "height": 900})
            page.get_by_role("button", name="Novo horário").click()

            # Exercita cancelamento e agendamento no app real; a camada HTTP é
            # interceptada em sitecustomize e não alcança o Xano.
            situacao_consulta = page.get_by_role("combobox", name="Alterar situação").first
            situacao_consulta.click()
            situacao_consulta.press("ArrowDown")
            situacao_consulta.press("Enter")
            page.wait_for_timeout(300)
            motivo_cancelamento = page.get_by_label("Motivo do cancelamento").first
            motivo_cancelamento.wait_for(state="visible")
            motivo_cancelamento.fill("Cancelamento de teste fictício")
            page.get_by_text("Confirmo o cancelamento", exact=True).first.click()
            page.get_by_role("button", name="Atualizar").first.click()
            page.get_by_text("Situação da consulta atualizada.").wait_for()
            page.get_by_role("button", name="›", exact=True).click()
            data_seguinte = (date.today() + timedelta(days=1)).strftime("%d/%m/%Y")
            page.get_by_text(f"{data_seguinte} · 0 consulta(s)", exact=True).wait_for()
            page.get_by_test_id("stBaseButton-primary").click()
            page.get_by_label("Paciente").wait_for()
            page.wait_for_timeout(300)
            page.screenshot(path=destino / "nova-consulta-desktop.png", full_page=True)
            assert page.get_by_label("Profissional").is_visible()
            assert page.get_by_label("Procedimentos (opcional)").is_visible()
            assert page.get_by_label("Observação administrativa (opcional)").is_visible()

            page.set_viewport_size({"width": 390, "height": 844})
            page.wait_for_timeout(300)
            page.screenshot(path=destino / "agenda-celular-topo.png")
            rolagens = page.evaluate("""() => [...document.querySelectorAll('*')]
              .filter(el => el.scrollHeight > el.clientHeight + 50)
              .map(el => ({tag: el.tagName, id: el.id, testid: el.getAttribute('data-testid'),
                classe: String(el.className).slice(0, 80), altura: el.clientHeight, conteudo: el.scrollHeight}))""")
            print("Contêineres roláveis:", rolagens)
            page.evaluate("""() => [...document.querySelectorAll('*')]
              .filter(el => el.scrollHeight > el.clientHeight + 50)
              .forEach(el => { el.scrollTop = el.scrollHeight; })""")
            page.screenshot(path=destino / "agenda-celular-conteudo.png")
            largura = page.evaluate("({viewport: document.documentElement.clientWidth, pagina: document.documentElement.scrollWidth})")
            assert largura["pagina"] <= largura["viewport"], f"Rolagem horizontal no celular: {largura}"

            # Usa o cliente REST real e respostas HTTP fictícias para completar
            # um cadastro antigo, salvar e reabrir a edição como Recepcionista.
            page.set_viewport_size({"width": 1365, "height": 900})
            page.get_by_role("button", name="Pacientes", exact=True).click()
            page.get_by_role("button", name="Editar", exact=True).first.click()
            dialogo = page.get_by_role("dialog")
            dialogo.wait_for()
            for campo in ("CPF *", "Celular *", "E-mail *"):
                assert dialogo.get_by_label(campo, exact=True).input_value() == ""
            page.screenshot(path=destino / "paciente-edicao-cadastro-antigo.png")
            dialogo.get_by_label("Nome completo *").fill("Paciente Fictícia Aurora Atualizada")
            dialogo.get_by_label("CPF *", exact=True).fill("52998224725")
            dialogo.get_by_label("Celular *", exact=True).fill("11911112222")
            dialogo.get_by_label("E-mail *", exact=True).fill("aurora.ficticia@example.invalid")
            dialogo.get_by_role("button", name="Salvar alterações").click()
            dialogo.wait_for(state="hidden")
            page.get_by_text("Os dados cadastrais do Paciente foram atualizados.", exact=True).wait_for()
            page.get_by_text("Paciente Fictícia Aurora Atualizada", exact=True).wait_for()
            page.get_by_role("button", name="Editar", exact=True).first.click()
            dialogo.wait_for()
            assert dialogo.get_by_label("E-mail *", exact=True).input_value() == "aurora.ficticia@example.invalid"
            dialogo.get_by_role("button", name="Cancelar", exact=True).click()
            dialogo.wait_for(state="hidden")
            browser.close()
    finally:
        processo.terminate()
        try:
            processo.wait(timeout=8)
        except subprocess.TimeoutExpired:
            processo.kill()
    print(f"Capturas fictícias salvas em: {destino}")


if __name__ == "__main__":
    main()
