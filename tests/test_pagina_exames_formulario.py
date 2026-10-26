"""Testes do formulário de solicitação de Exames sem chamadas de rede."""

from pathlib import Path

from streamlit.testing.v1 import AppTest


def abrir(falha=None):
    script = f'''\
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace
import sys
import streamlit as st
sys.path.insert(0, {str(Path(__file__).resolve().parents[1])!r})
from sorrisomais.api import Credencial, ErroAcesso
from sorrisomais import sessao
from sorrisomais.pagina_exames_xano import renderizar
class ClienteFalso:
    def _request(self, method, route, **kwargs):
        if method == 'GET':
            return {{'exames': []}}
        st.session_state['solicitacao'] = kwargs['payload']
        return {{'exame': {{'id': 71}}}}
    def listar_opcoes_agenda(self, token):
        if {falha!r} == 'opcoes':
            raise ErroAcesso('Detalhe interno', 503)
        if {falha!r} == 'pacientes_vazios':
            return {{'pacientes': [], 'profissionais': []}}
        return {{'pacientes': [{{'id': 11, 'nome': 'Paciente Fictício Aurora'}},
                             {{'id': 12, 'nome': 'Paciente Fictício Bento'}}],
                'profissionais': []}}
    def listar_consultas(self, token):
        if {falha!r} == 'consultas':
            raise ErroAcesso('Detalhe interno', 503)
        inicio = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        return [{{'id': 31, 'paciente_id': 11, 'paciente_nome': 'Paciente Fictício Aurora',
                 'situacao': 'Confirmada', 'inicio_em': inicio}},
                {{'id': 32, 'paciente_id': 12, 'paciente_nome': 'Paciente Fictício Bento',
                 'situacao': 'Confirmada', 'inicio_em': inicio}}]
st.session_state[sessao.CHAVE] = Credencial('token-ficticio', datetime.now(timezone.utc) + timedelta(hours=1))
renderizar(ClienteFalso(), SimpleNamespace(perfis=('profissional',)))
'''
    return AppTest.from_string(script, default_timeout=10).run()


def test_seletores_legiveis_filtram_consulta_e_enviam_ids():
    app = abrir()
    assert not app.exception
    assert "Paciente Fictício Aurora" in app.selectbox(key="exame-paciente").options
    assert "Paciente Fictício Bento" in app.selectbox(key="exame-paciente").options
    opcoes_consulta = app.selectbox(key="exame-consulta").options
    assert len(opcoes_consulta) == 1
    assert "Paciente Fictício Aurora" in opcoes_consulta[0]
    assert "/" in opcoes_consulta[0] and ":" in opcoes_consulta[0]

    app.text_input[0].input("Radiografia fictícia").run()
    next(button for button in app.button if button.label == "Solicitar exame").click().run()
    assert app.session_state["solicitacao"]["paciente_id"] == 11
    assert app.session_state["solicitacao"]["consulta_id"] == 31


def test_trocar_paciente_filtra_consultas_correspondentes():
    app = abrir()
    app.selectbox(key="exame-paciente").select(12).run()
    assert len(app.selectbox(key="exame-consulta").options) == 1
    assert "Paciente Fictício Bento" in app.selectbox(key="exame-consulta").options[0]
    assert app.selectbox(key="exame-consulta").value == 32


def test_erro_ao_carregar_dados_impede_formulario():
    app = abrir("consultas")
    assert not app.exception
    assert any("Não foi possível carregar Pacientes e Consultas" in item.value
               for item in app.error)
    assert not any(item.label == "Solicitar exame" for item in app.button)


def test_lista_vazia_apresenta_orientacao_sem_formulario():
    app = abrir("pacientes_vazios")
    assert not app.exception
    assert any("Cadastre Pacientes ativos" in item.value for item in app.info)
    assert not any(item.label == "Solicitar exame" for item in app.button)
