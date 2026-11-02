"""Segurança dos vetores incorporados, procedência e renderização decorativa."""
import hashlib
import json
import xml.etree.ElementTree as ET

import pytest

from sorrisomais.icones import PASTA_ICONES, estilos_icones, icone_html, icone_metrica, svg_icone, validar_svg


def test_recursos_correspondem_ao_manifesto_revisado():
    origem = json.loads((PASTA_ICONES / "origem.json").read_text(encoding="utf-8"))
    assert origem["commit"] == "64c0e165c3ce6d5c9d7329acf5762306f86d6b1d"
    assert set(origem["sha256"]) == {p.name for p in PASTA_ICONES.glob("*.svg")}
    for nome, esperado in origem["sha256"].items():
        conteudo = (PASTA_ICONES / nome).read_bytes()
        assert hashlib.sha256(conteudo).hexdigest() == esperado
        validar_svg(conteudo.decode())
    assert "MIT License" in (PASTA_ICONES / "LICENSE").read_text()


@pytest.mark.parametrize("corpo", [
    '<script>alert(1)</script>', '<foreignObject/>', '<image href="https://exemplo.invalid/rastreio"/>',
    '<path d="M0 0" onclick="alert(1)"/>', '<path d="M0 0" fill="url(https://exemplo.invalid)"/>',
    '<path d="M0 0" style="color:red"/>', '<a href="javascript:alert(1)"/>',
])
def test_rejeita_conteudo_ativo(corpo):
    with pytest.raises(ValueError):
        validar_svg(f'<svg xmlns="http://www.w3.org/2000/svg">{corpo}</svg>')


def test_rejeita_entidades_e_caminhos_externos():
    with pytest.raises(ValueError):
        validar_svg('<!DOCTYPE svg [<!ENTITY x SYSTEM "file:///segredo">]><svg/>')
    for nome in ("../segredo", "/tmp/segredo", "https://exemplo.invalid", "home.svg"):
        with pytest.raises(ValueError):
            svg_icone(nome)


def test_icone_e_decorativo_e_herda_cor():
    raiz = ET.fromstring(icone_html("home", 'teste" onclick="falha'))
    assert raiz.attrib["aria-hidden"] == "true"
    assert raiz.attrib["stroke"] == "currentColor"
    assert "onclick" not in raiz.attrib
    assert '<svg ' in icone_metrica("Atendimentos")


def test_mascaras_locais_nao_injetam_scripts_ou_ocultam_rotulos():
    estilos = estilos_icones()
    assert "data:image/svg+xml;base64," in estilos
    assert "<script" not in estilos
    assert "https://" not in estilos
    assert 'button p {display:none' not in estilos
