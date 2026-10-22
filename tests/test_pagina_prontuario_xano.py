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
        st.session_state["_chamadas_api_prontuario"] = st.session_state.get("_chamadas_api_prontuario", 0) + 1
        {f'raise ErroAcesso("Falha segura.", {erro})' if erro else f'return {consultas!r}'}
    def listar_registros_clinicos(self, token):
        st.session_state["_chamadas_api_prontuario"] = st.session_state.get("_chamadas_api_prontuario", 0) + 1
        {f'raise ErroAcesso("Falha segura.", {erro})' if erro else f'return {registros!r}'}
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
    assert "ID 13" in str(app.selectbox[0].options)
    assert "Paciente 13" not in str(app.selectbox[0].options)
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


def test_erro_403_mantem_sessao_e_mensagem_de_permissao():
    app = abrir([], [], erro=403)
    assert not app.exception
    assert any("Falha segura." in item.value for item in app.error)
    assert "credencial" in app.session_state


def test_erro_401_limpa_sessao_e_pede_novo_login():
    app = abrir([], [], erro=401)
    assert not app.exception
    assert any("Sua sessão expirou. Entre novamente." in item.value for item in app.error)
    assert "credencial" not in app.session_state


def test_rerun_ao_trocar_paciente_reutiliza_gets_da_sessao():
    consultas = [
        {"paciente_id": 12, "paciente_nome": "Paciente FictÃ­cia Aurora"},
        {"paciente_id": 13, "paciente_nome": "Paciente FictÃ­cio Bruno"},
    ]
    app = abrir(consultas, [])
    assert app.session_state["_chamadas_api_prontuario"] == 2

    app.selectbox[0].set_value(13).run()

    assert not app.exception
    assert app.session_state["_chamadas_api_prontuario"] == 2


def test_falha_na_api_nao_e_cacheada_e_pode_ser_tentada_novamente():
    app = abrir([], [], erro=503)
    assert app.session_state["_chamadas_api_prontuario"] == 1

    app.run()

    assert not app.exception
    assert app.session_state["_chamadas_api_prontuario"] == 2
