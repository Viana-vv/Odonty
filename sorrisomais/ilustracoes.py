"""Componentes visuais reutilizáveis das ilustrações Sorriso Mais."""

from base64 import b64encode
from pathlib import Path
from html import escape
from functools import lru_cache

import streamlit as st


RAIZ = Path(__file__).resolve().parents[1]
PASTA_MASCOTES = RAIZ / "assets" / "mascotes-tratados"
MARCA_MASCOTE = PASTA_MASCOTES / "04-profissionais.png"


@lru_cache(maxsize=16)
def _data_uri(nome: str) -> str:
    caminho = PASTA_MASCOTES / nome
    dados = b64encode(caminho.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{dados}"


def banner_contextual(mascote: str, etiqueta: str, titulo: str, texto: str, *, classe: str = "") -> None:
    """Renderiza um banner com ondas, texto e mascote contextual."""
    imagem = _data_uri(mascote)
    etiqueta, titulo, texto, classe = map(escape, (etiqueta, titulo, texto, classe))
    st.html(f"""
    <section class="banner-contextual {classe}">
      <div class="banner-contextual-conteudo">
        <span class="banner-contextual-etiqueta">{etiqueta}</span>
        <h2>{titulo}</h2>
        <p>{texto}</p>
      </div>
      <div class="banner-contextual-arte"><span></span><img src="{imagem}" alt="" /></div>
    </section>
    """)


def ilustracao_contextual(nome: str) -> None:
    """Arte compacta para estados e formulários, sem substituir mensagens acessíveis."""
    st.html(f'<div class="ilustracao-contextual"><img src="{_data_uri(nome)}" alt="" /></div>')


def marca_html() -> str:
    """Assinatura Sorriso+ compartilhada, sem a imagem antiga com fundo quadrado."""
    return (f'<div class="assinatura-sorriso"><img src="{_data_uri(MARCA_MASCOTE.name)}" '
            'alt="Mascote odontológico Sorriso+"><div class="assinatura-texto">'
            '<strong>Sorriso<span>+</span></strong><small>Clínica Odontológica</small></div></div>')


def icone_metrica(rotulo: str) -> str:
    """Ícones de traço coerentes com o kit, sem glifos dependentes da fonte."""
    desenhos = {
        "Consultas hoje": '<rect x="4" y="6" width="24" height="22" rx="4"/><path d="M4 13h24M10 3v6M22 3v6m-11 9h10m-10 5h6"/>',
        "Pacientes ativos": '<circle cx="12" cy="10" r="4"/><path d="M3 27v-4a9 9 0 0 1 18 0v4m0-21a4 4 0 0 1 0 8m4 4a9 9 0 0 1 4 9"/>',
        "Atendimentos": '<path d="M9 4c-6 0-6 9-3 14 1 3 1 10 4 10s2-10 6-10 3 10 6 10 3-7 4-10c3-5 3-14-3-14-4 0-5 3-7 3S13 4 9 4Z"/>',
        "Próxima consulta": '<circle cx="16" cy="16" r="12"/><path d="M16 8v8l6 4"/>',
    }
    desenho = desenhos.get(rotulo, '<path d="m7 16 6 6L26 8"/>')
    return f'<span class="icone-metrica"><svg viewBox="0 0 32 32" width="28" height="28" fill="none" stroke="currentColor" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{desenho}</svg></span>'
