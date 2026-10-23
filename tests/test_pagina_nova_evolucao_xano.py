"""Testes da tela de nova evolução sem chamadas de rede."""

from pathlib import Path

from streamlit.testing.v1 import AppTest


def abrir(*, perfis=("profissional",), falha=None):
    raiz = Path(__file__).resolve().parents[1]
    script = f'''\
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
import sys
import streamlit as st
sys.path.insert(0, {str(raiz)!r})
from sorrisomais.api import Credencial, ErroAcesso
from sorrisomais.pagina_nova_evolucao_xano import renderizar
from sorrisomais import pagina_nova_evolucao_xano as pagina
st.session_state["credencial"] = Credencial("token-ficticio", datetime.now(timezone.utc) + timedelta(hours=1))
st.session_state[pagina._CHAVE_ABERTO] = True
class ClienteFalso:
    def registrar_clinico(self, token, paciente_id, conteudo, *, consulta_id=None):
        st.session_state["_registro_enviado"] = {{"paciente_id": paciente_id, "conteudo": conteudo, "consulta_id": consulta_id}}
        {f'raise ErroAcesso("Falha segura.", {falha})' if falha else 'return {"id": 42}'}
renderizar(ClienteFalso(), SimpleNamespace(nome="Dra. Fictícia", perfis={perfis!r}), [
    {{"id": 17, "paciente_id": 3, "paciente_nome": "Paciente Fictícia", "profissional_id": 9, "profissional_nome": "Dra. Fictícia", "inicio_em": "2026-10-10T10:00:00Z", "situacao": "Realizada"}},
])
'''
    return AppTest.from_string(script, default_timeout=20).run()


def test_formulario_limita_perfil_e_nao_expoe_data_ou_procedimento_gravavel():
    app = abrir()
    assert not app.exception
    assert any("Consulta relacionada (opcional)" in item.label for item in app.selectbox)
    assert any("Evolução e observações" in item.label for item in app.text_area)
    assert not any("Procedimento" in item.label for item in app.selectbox)
    assert any("Profissional responsável: Dra. Fictícia" in item.value for item in app.caption)


def test_perfil_sem_permissao_nao_renderiza_formulario():
    app = abrir(perfis=("recepcionista",))
    assert not app.exception
    assert any("Somente Profissional autorizado" in item.value for item in app.warning)
    assert not app.text_area


def test_conteudo_vazio_nao_chama_api():
    app = abrir()
    app.button[1].click().run()
    assert not app.exception
    assert any("Informe a evolução clínica" in item.value for item in app.error)
    assert "_registro_enviado" not in app.session_state


def test_envia_contrato_existente_e_invalida_cache_apos_sucesso():
    app = abrir()
    app.text_area[0].set_value("Evolução fictícia do atendimento")
    app.selectbox[1].set_value(17)
    app.button[1].click().run()
    assert not app.exception
    assert app.session_state["_registro_enviado"] == {
        "paciente_id": 3,
        "conteudo": "Evolução fictícia do atendimento",
        "consulta_id": 17,
    }
    assert "Registro Clínico salvo no Prontuário." in app.session_state["prontuario_aviso"]
    assert "prontuario_historico_cache" not in app.session_state


def test_erro_de_permissao_nao_apresenta_detalhes_clinicos():
    app = abrir(falha=403)
    app.text_area[0].set_value("Conteúdo clínico fictício")
    app.button[1].click().run()
    assert not app.exception
    assert any("não tem permissão" in item.value for item in app.error)
    assert not any("Falha segura" in item.value for item in app.error)


def test_sessao_expirada_limpa_credencial():
    app = abrir(falha=401)
    app.text_area[0].set_value("Conteúdo clínico fictício")
    app.button[1].click().run()
    assert not app.exception
    assert any("Sua sessão expirou" in item.value for item in app.error)
    assert "credencial" not in app.session_state
