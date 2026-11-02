"""Componentes visuais reutilizáveis das ilustrações Sorriso Mais."""

from base64 import b64encode
from pathlib import Path
from html import escape
from functools import lru_cache

import streamlit as st
from .icones import icone_metrica


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
