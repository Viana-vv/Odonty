"""Entry point Streamlit independente para o autoatendimento do Paciente."""

from pathlib import Path

import streamlit as st

from sorrisomais import autoatendimento_paciente, sessao_paciente
from sorrisomais.api import ClienteXano, ErroAcesso
from sorrisomais.config import Configuracao, ConfiguracaoInvalida

RAIZ = Path(__file__).parent
st.set_page_config(page_title="Área do Paciente · Sorriso+", page_icon=str(RAIZ / "assets" / "mascote-sorriso.png"), layout="wide")
st.html((RAIZ / "assets" / "estilos.css").read_text(encoding="utf-8"))

try:
    cliente = ClienteXano(Configuracao.do_ambiente())
except ConfiguracaoInvalida as erro:
    cliente = None
    sessao_paciente.limpar(st.session_state)
    st.error(str(erro))

if cliente:
    try:
        autoatendimento_paciente.renderizar(cliente)
    except ErroAcesso as erro:
        sessao_paciente.limpar(st.session_state)
        st.session_state["paciente_aviso"] = str(erro)
        st.rerun()
