"""Verificações da tela de Prontuário usando AppTest e dados sem rede."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest


def abrir(consultas, registros, *, perfis=("profissional",), erro=None):
    script = f'''\
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys
from types import SimpleNamespace
import streamlit as st
sys.path.insert(0, {str(Path(__file__).resolve().parents[1])!r})
from sorrisomais.api import Credencial, ErroAcesso
from sorrisomais import sessao
from sorrisomais.pagina_prontuario_xano import renderizar

st.session_state[sessao.CHAVE] = Credencial("token-ficticio", datetime.now(timezone.utc) + timedelta(hours=1))
class ClienteFalso:
    def listar_consultas(self, token):
        {f'raise ErroAcesso("Falha segura.", 403)' if erro else f'return {consultas!r}'}
    def listar_registros_clinicos(self, token):
        {f'raise ErroAcesso("Falha segura.", 403)' if erro else f'return {registros!r}'}
renderizar(ClienteFalso(), SimpleNamespace(perfis={perfis!r}))
'''
    return AppTest.from_string(script, default_timeout=20).run()


def test_historico_mostra_apenas_conteudo_retornado_para_paciente_selecionado():
    consultas = [{"paciente_id": 12, "paciente_nome": "Paciente Fictícia Aurora"}]
    registros = [
        {"id": 8, "paciente_id": 12, "conteudo": "Evolução fictícia", "registrado_em": "2026-10-10T12:00:00Z"},
        {"id": 9, "paciente_id": 13, "conteudo": "Outro registro fictício", "registrado_em": "2026-10-09T12:00:00Z"},
    ]
    app = abrir(consultas, registros)
    assert not app.exception
    assert "Paciente Fictícia Aurora" in str(app.selectbox[0].options)
    assert any("Evolução fictícia" in item.value for item in app.markdown)
    assert not any("Outro registro fictício" in item.value for item in app.markdown)


def test_perfil_administrativo_nao_carrega_dados_clinicos():
    app = abrir([], [], perfis=("recepcionista",))
    assert not app.exception
    assert any("não está disponível para este perfil" in item.value for item in app.warning)


@pytest.mark.parametrize(
    ("consultas", "registros", "esperado"),
    [([], [], "Não há Pacientes"), ([{"paciente_id": 2, "paciente_nome": "Paciente Fictícia"}], [], "ainda não possui Registros Clínicos")],
)
def test_estados_vazios(consultas, registros, esperado):
    app = abrir(consultas, registros)
    assert not app.exception
    assert any(esperado in item.value for item in app.info)


def test_falha_api_apresenta_mensagem_segura():
    app = abrir([], [], erro=True)
    assert not app.exception
    assert any("Falha segura." in item.value for item in app.error)
