"""Vetores Regen locais e decorativos; controles continuam nativos do Streamlit."""
from base64 import b64encode
from functools import lru_cache
from html import escape
from pathlib import Path
import re
import xml.etree.ElementTree as ET

PASTA_ICONES = Path(__file__).resolve().parents[1] / "assets/icones/regen"
_ATRIBUTOS = {"width", "height", "viewBox", "fill", "stroke", "stroke-width",
              "stroke-linecap", "stroke-linejoin", "aria-hidden", "d", "opacity"}


def validar_svg(conteudo: str) -> str:
    """Rejeita tudo que não seja o vocabulário gráfico usado pelos vetores auditados."""
    if "<!" in conteudo or "<?" in conteudo:
        raise ValueError("Declaração SVG não permitida.")
    raiz = ET.fromstring(conteudo)
    if raiz.tag != "{http://www.w3.org/2000/svg}svg":
        raise ValueError("Raiz SVG inválida.")
    for elemento in raiz.iter():
        if elemento.tag not in {"{http://www.w3.org/2000/svg}svg", "{http://www.w3.org/2000/svg}path"}:
            raise ValueError("Elemento SVG não permitido.")
        if elemento.text and elemento.text.strip():
            raise ValueError("Texto SVG não permitido.")
        for nome, valor in elemento.attrib.items():
            if nome not in _ATRIBUTOS or re.search(r"url\s*\(|javascript:|https?:|data:|[<>]", valor, re.I):
                raise ValueError("Atributo SVG não permitido.")
    return conteudo.strip()


@lru_cache(maxsize=64)
def svg_icone(nome: str) -> str:
    if not re.fullmatch(r"[a-z]+(?:-[a-z]+)*", nome):
        raise ValueError("Nome de ícone inválido.")
    return validar_svg((PASTA_ICONES / f"{nome}.svg").read_text(encoding="utf-8"))


def icone_html(nome: str, classe: str = "") -> str:
    return svg_icone(nome).replace('<svg ', f'<svg class="icone-regen {escape(classe, quote=True)}" ', 1)


def icone_metrica(rotulo: str) -> str:
    nome = {"Consultas hoje": "calendar", "Atendimentos": "clipboard-check",
            "Pacientes ativos": "users", "Próxima consulta": "clock",
            "Confirmadas": "calendar-check", "Prontuários": "file-text"}.get(rotulo, "circle-check")
    return f'<span class="icone-metrica">{icone_html(nome)}</span>'


def _mascara(nome: str) -> str:
    return 'url("data:image/svg+xml;base64,' + b64encode(svg_icone(nome).encode()).decode() + '")'


@lru_cache(maxsize=1)
def estilos_icones() -> str:
    """Máscaras herdam cor sem modificar labels, callbacks ou áreas de clique."""
    botoes = ':is([data-testid="stButton"],[data-testid="stFormSubmitButton"],[data-testid="stDownloadButton"],[data-testid="stLinkButton"])'
    css = [f'{botoes} button::before,{botoes} a::before,[data-testid="stPopoverButton"]::before {{content:"";display:inline-block;flex:0 0 20px;width:20px;height:20px;background:currentColor;mask:var(--icone-acao,{_mascara("arrow-right")}) center/contain no-repeat;}}',
           f'{botoes} [data-testid="stIconMaterial"],[data-testid="stPopoverButton"] [data-testid="stIconMaterial"] {{display:none;}}',
           '.icone-regen {display:inline-block;width:24px;height:24px;flex-shrink:0;vertical-align:middle;}',
           '.icone-metrica .icone-regen {width:26px;height:26px;}.icone-procedimento .icone-regen {width:28px;height:28px;}',
           f'{botoes} button {{column-gap:8px;}}',
           '.st-key-menu-equipe [data-testid="stButton"] button>div {flex:1;justify-content:flex-start;text-align:left;}',
           f'[data-testid="stFormSubmitButton"] {{ --icone-acao:{_mascara("save")};}}',
           f'.st-key-formulario [data-testid="stFormSubmitButton"],.st-key-portal-paciente-formulario [data-testid="stFormSubmitButton"] {{ --icone-acao:{_mascara("log-in")};}}',
           f'[data-testid="stPopover"] {{ --icone-acao:{_mascara("adjustments")};}}']
    # Chaves já existentes: a escolha visual não muda a identidade de nenhum widget.
    grupos = {
        "file-text": ("prontuario",), "calendar": ("agenda-atalho", "-ver-agenda", "inicio-agenda", "abrir-agenda"),
        "refresh": ("atualizar", "recarregar", "tentar", "retry"),
        "plus": ("-novo", "-nova", "_novo", "_nova", "adicionar", "cadastrar"),
        "save": ("salvar", "gravar"), "check": ("confirmar", "concluir", "realizar"),
        "x": ("cancelar", "fechar"), "pencil": ("editar", "edicao"),
        "arrow-left": ("anterior", "voltar"), "arrow-right": ("seguinte", "proximo"),
    }
    for nome, termos in grupos.items():
        seletores = ','.join(f':where([class*="st-key-"])[class*="{termo}"]' for termo in termos)
        css.append(f'{seletores} {{ --icone-acao:{_mascara(nome)};}}')
    exatos = {"menu-inicio": "home", "menu-agenda": "calendar", "menu-pacientes": "users",
              "menu-profissionais": "user", "menu-prontuarios": "file-text", "menu-procedimentos": "tool",
              "menu-exames": "scan", "menu-reagendar_consulta": "repeat", "menu-contas_acesso": "shield-check",
              "menu-cadastrar-paciente": "user-plus", "menu-cadastrar-profissional": "user-plus", "sair": "log-out", "paciente-sair": "log-out"}
    for chave, nome in exatos.items():
        css.append(f'.st-key-{chave} {{ --icone-acao:{_mascara(nome)};}}')
        if chave.startswith("menu-"):
            css.append(f'.st-key-demo-nav-{chave[5:]} {{ --icone-acao:{_mascara(nome)};}}')
    css.extend([
        '[class*="st-key-"][class*="fechar"] button p,.st-key-agenda-anterior button p,.st-key-agenda-proximo button p {position:absolute;width:1px;height:1px;overflow:hidden;clip-path:inset(50%);white-space:nowrap;}',
        f'.st-key-visao-geral h1::after {{content:"";display:inline-block;vertical-align:middle;margin-left:12px;width:26px;height:26px;background:var(--verde);mask:{_mascara("heart")} center/contain no-repeat;}}',
    ])
    # Indicadores e controles internos mantêm o elemento interativo original.
    controles = {
        '[data-testid="stAlert"] [data-testid="stIconMaterial"]': "info-circle",
        '[data-testid="stAlert"][data-baseweb="notification"] [data-testid="stIconMaterial"]': "info-circle",
        '[data-testid="stExpander"] summary [data-testid="stIconMaterial"]': "chevron-right",
        '[data-testid="stExpander"] details[open]>summary [data-testid="stIconMaterial"]': "chevron-down",
        '[data-baseweb="select"] svg': "chevron-down",
        '[data-testid="stSelectbox"] button[aria-haspopup="listbox"] svg': "chevron-down",
        '[data-testid="stTimeInput"] button[aria-haspopup="listbox"] svg': "chevron-down",
        '[data-testid="stDateInput"] button svg': "calendar",
        '[data-testid="stTextInput"] button svg': "eye",
        '[data-testid="stTextInput"]:has(input[type="text"]) button svg': "eye-off",
        '[data-testid="stTextInput"] button [data-testid="stIconMaterial"]': "eye",
        '[data-testid="stTextInput"] button[aria-pressed="true"] [data-testid="stIconMaterial"]': "eye-off",
        '[data-testid="stNumberInputStepUp"] svg': "plus",
        '[data-testid="stNumberInputStepDown"] svg': "minus",
        '[data-testid="stCheckbox"] svg': "check",
        '[data-testid="stDialog"] button[aria-label="Close"] svg': "x",
        '[data-testid="stDialog"] button[aria-label="Close"] [data-testid="stIconMaterial"]': "x",
        '[data-testid="stDateInputCalendar"] button[slot="previous"] svg': "arrow-left",
        '[data-testid="stDateInputCalendar"] button[slot="next"] svg': "arrow-right",
        '[data-testid="stDateInputCalendar"] button[aria-haspopup="listbox"] svg': "chevron-down",
        '[role="option"] svg': "check",
        'a[aria-label="Link to heading"] svg': "link",
        '[data-testid="stSpinnerIcon"]': "refresh",
    }
    for seletor, nome in controles.items():
        css.append(f'{seletor} {{width:20px!important;height:20px!important;min-width:20px;font-size:0!important;background:currentColor;mask:{_mascara(nome)} center/contain no-repeat;}}{seletor}>* {{visibility:hidden;}}')
    css.append('[data-testid="stCheckbox"] svg {width:12px!important;height:12px!important;min-width:12px;}')
    css.append('[data-testid="stSpinnerIcon"] {border:0!important;border-radius:0;}')
    for tipo, nome in {"Info": "info-circle", "Success": "circle-check", "Warning": "alert-triangle", "Error": "circle-alert"}.items():
        css.append(f'[data-testid="stAlertContent{tipo}"] {{display:flex;gap:10px;align-items:flex-start;}}[data-testid="stAlertContent{tipo}"]::before {{content:"";flex:0 0 20px;width:20px;height:20px;margin-top:2px;background:currentColor;mask:{_mascara(nome)} center/contain no-repeat;}}')
    return '<style>' + '\n'.join(css) + '</style>'
