from pathlib import Path
import re

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[2]
ENDPOINT = ROOT / "backend/xano/api/sorriso_acesso/auth/recuperacao-senha_POST.xs"
MASCOTE = ROOT / "assets/mascote-sorriso-email.png"


def _render_template(otp="012304", minutos="7"):
    source = ENDPOINT.read_text(encoding="utf-8-sig")
    template = source.split('set:"type":"text/html"|set:"value":("', 1)[1].split('"|sprintf:', 1)[0]
    values = [*otp, otp, minutos]
    for value in values:
        template = template.replace("%s", value, 1)
    template = template.replace("%%", "%")
    return template


def test_template_otp_renderiza_em_desktop_e_celular():
    html = _render_template()
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            page = browser.new_page(viewport={"width": 320, "height": 844})
            page.route(
                "https://raw.githubusercontent.com/**/mascote-sorriso-email.png",
                lambda route: route.fulfill(path=str(MASCOTE), content_type="image/png"),
            )
            page.set_content(html, wait_until="load")
            assert page.locator("img[alt='Mascote Sorriso+']").count() == 1
            assert page.locator("img").evaluate("img => img.complete && img.naturalWidth > 0")
            assert page.locator("div").filter(has_text=re.compile(r"^[0-9]$")).all_text_contents() == list("012304")
            assert page.locator("text=Código para copiar: 012304").count() == 1
            assert page.locator("text=Este código é válido por 7 minutos.").count() == 1
            for largura in (320, 390, 600, 1440):
                page.set_viewport_size({"width": largura, "height": 900})
                assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
            codigo_selecionado = page.locator("strong").filter(has_text="012304").evaluate(
                "element => { const r = document.createRange(); r.selectNodeContents(element); "
                "const s = window.getSelection(); s.removeAllRanges(); s.addRange(r); return s.toString(); }"
            )
            assert codigo_selecionado == "012304"
        finally:
            browser.close()
