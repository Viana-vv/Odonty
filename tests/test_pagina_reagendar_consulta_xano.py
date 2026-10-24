"""Verificação da interface administrativa com contratos simulados, sem rede."""
from datetime import date, timedelta
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest


def _abrir(*, perfil="recepcionista", falha=None, token=True):
    fonte = f'''
from types import SimpleNamespace
from datetime import date, timedelta
import sys
import streamlit as st
sys.path.insert(0, {str(Path(__file__).resolve().parents[1])!r})
from sorrisomais.api import ClienteXano, ErroAcesso
from sorrisomais import sessao
from sorrisomais.pagina_reagendar_consulta_xano import renderizar

class ClienteFicticio(ClienteXano):
    def __init__(self):
        pass
    def listar_opcoes_agenda(self, token):
        st.session_state['leituras_opcoes'] = st.session_state.get('leituras_opcoes', 0) + 1
        if {falha!r} == 'opcoes_401':
            raise ErroAcesso('Sua sessão expirou.', 401)
        if {falha!r} == 'opcoes_403':
            raise ErroAcesso('Sua conta não tem permissão.', 403)
        if {falha!r} == 'sem_opcoes':
            return {{'pacientes': [], 'profissionais': []}}
        return {{'pacientes': [{{'id': 1, 'nome': 'Paciente Fictício'}}, {{'id': 2, 'nome': 'Outro Paciente Fictício'}}],
                'profissionais': [{{'id': 8, 'nome': 'Profissional Fictício'}}, {{'id': 9, 'nome': 'Outro Profissional Fictício'}}]}}
    def listar_consultas(self, token, paciente_id=None):
        if {falha!r} == 'consultas_503':
            raise ErroAcesso('Detalhe interno secreto', 503)
        if {falha!r} == 'sem_consultas':
            return []
        if st.session_state.get('enviada'):
            return []
        dia = date.today() + timedelta(days=1)
        dados = {{'id': 10 if paciente_id == 1 else 20, 'paciente_id': paciente_id,
                 'profissional_id': 8, 'profissional_nome': 'Profissional Fictício',
                 'inicio_em': dia.isoformat() + 'T10:00:00-03:00',
                 'disponibilidade_id': 3, 'situacao': 'Confirmada'}}
        return [dados, dict(dados), dict(dados, id=99, situacao='Realizada'),
                dict(dados, id=98, disponibilidade_id=None)]
    def listar_disponibilidades(self, token, profissional_id, inicio, fim):
        if {falha!r} == 'horarios_401':
            raise ErroAcesso('Sua sessão expirou.', 401)
        if {falha!r} == 'sem_horarios':
            return []
        dia = date.fromisoformat(inicio[:10])
        identificador = 5 if profissional_id == 8 else 6
        return [{{'id': identificador, 'situacao': 'disponivel',
                  'inicio': dia.isoformat() + 'T14:00:00-03:00',
                  'fim': dia.isoformat() + 'T15:00:00-03:00'}},
                {{'id': 3, 'situacao': 'disponivel'}}, {{'id': 7, 'situacao': 'bloqueado'}}]
    def _request(self, metodo, rota, **kwargs):
        st.session_state['chamadas_mutacao'] = st.session_state.get('chamadas_mutacao', 0) + 1
        if {falha!r} == 'conflito':
            raise ErroAcesso('Detalhe interno secreto', 409)
        if {falha!r} == 'envio_401':
            raise ErroAcesso('Sua sessão expirou.', 401)
        st.session_state['enviada'] = (metodo, rota, kwargs['payload'])
        return {{'consulta_original': {{'id': 10, 'paciente_id': 1, 'profissional_id': 8, 'disponibilidade_id': 3, 'situacao': 'Cancelada'}},
                'consulta': {{'id': 11, 'paciente_id': 1, 'profissional_id': 8, 'disponibilidade_id': kwargs['payload']['disponibilidade_id'], 'situacao': 'Agendada'}},
                'reagendamento_id': 1}}

if {token!r}:
    st.session_state[sessao.CHAVE] = SimpleNamespace(token='token-ficticio')
st.session_state[sessao.CHAVE_CONTA] = SimpleNamespace(perfis=({perfil!r},))
renderizar(ClienteFicticio(), SimpleNamespace(perfis=({perfil!r},)))
'''
    return AppTest.from_string(fonte, default_timeout=10).run()


def _selecionar_consulta(app):
    app.selectbox(key="reagendar-consulta-paciente").select(1).run()
    app.selectbox(key="reagendar-consulta-consulta").select(10).run()
    return app


def _enviar(app):
    app.selectbox(key="reagendar-consulta-horario").select(5).run()
    app.text_area(key="reagendar-consulta-justificativa").input("Solicitação fictícia").run()
    next(item for item in app.button if item.label == "Reagendar consulta").click().run()
    return app


@pytest.mark.parametrize("perfil", ["administrador", "recepcionista"])
def test_sucesso_confirma_uma_operacao_e_limpa_selecao(perfil):
    app = _enviar(_selecionar_consulta(_abrir(perfil=perfil)))
    assert not app.exception
    assert any("Consulta reagendada" in item.value for item in app.success)
    assert app.session_state["enviada"] == (
        "POST", "/consultas/10/reagendamento",
        {"disponibilidade_id": 5, "justificativa": "Solicitação fictícia"},
    )
    assert app.session_state["chamadas_mutacao"] == 1
    assert app.selectbox(key="reagendar-consulta-paciente").value is None
    assert app.session_state["leituras_opcoes"] == 2


def test_seletor_deduplica_consultas_e_omite_encerradas_legadas_e_horario_original():
    app = _selecionar_consulta(_abrir())
    assert not app.exception
    assert len(app.selectbox(key="reagendar-consulta-consulta").options) == 1
    assert app.selectbox(key="reagendar-consulta-horario").options == ["14:00 – 15:00"]
    assert app.session_state["leituras_opcoes"] == 1


@pytest.mark.parametrize("perfil", ["paciente", "profissional"])
def test_perfil_sem_permissao_nao_faz_leituras(perfil):
    app = _abrir(perfil=perfil)
    assert not app.exception
    assert any("não tem permissão" in item.value for item in app.error)
    assert not app.selectbox
    assert "leituras_opcoes" not in app.session_state


def test_credencial_ausente_nao_consulta_api():
    app = _abrir(token=False)
    assert any("sessão expirou" in item.value for item in app.error)
    assert "leituras_opcoes" not in app.session_state


@pytest.mark.parametrize("falha", ["opcoes_401", "horarios_401", "envio_401"])
def test_expiracao_limpa_credencial_em_todas_as_etapas(falha):
    app = _abrir(falha=falha)
    if falha != "opcoes_401":
        _selecionar_consulta(app)
    if falha == "envio_401":
        _enviar(app)
    assert not app.exception
    assert any("sessão expirou" in item.value for item in app.error)
    assert "credencial" not in app.session_state
    assert "conta_acesso_cache" not in app.session_state
    assert not app.success


def test_403_mantem_sessao_e_informa_permissao():
    app = _abrir(falha="opcoes_403")
    assert any("não tem permissão" in item.value for item in app.error)
    assert "credencial" in app.session_state


def test_conflito_nao_confirma_nem_repete_mutacao():
    app = _enviar(_selecionar_consulta(_abrir(falha="conflito")))
    assert not app.exception
    assert not app.success
    assert any("A Consulta ou o horário mudou" in item.value for item in app.error)
    assert app.session_state["chamadas_mutacao"] == 1
    assert app.text_area(key="reagendar-consulta-justificativa").value == "Solicitação fictícia"
    assert "nova-consulta-cache-leituras" not in app.session_state


def test_horario_e_justificativa_obrigatorios_nao_enviam_mutacao():
    app = _selecionar_consulta(_abrir())
    enviar = lambda: next(item for item in app.button if item.label == "Reagendar consulta").click().run()
    enviar()
    assert any("Selecione um horário" in item.value for item in app.error)
    app.selectbox(key="reagendar-consulta-horario").select(5).run()
    enviar()
    assert any("Informe a justificativa" in item.value for item in app.error)
    assert "chamadas_mutacao" not in app.session_state


@pytest.mark.parametrize("filtro", ["profissional", "data", "paciente"])
def test_mudanca_de_filtro_limpa_horario_anterior(filtro):
    app = _selecionar_consulta(_abrir())
    app.selectbox(key="reagendar-consulta-horario").select(5).run()
    if filtro == "data":
        app.date_input(key="reagendar-consulta-data").set_value(date.today() + timedelta(days=3)).run()
    else:
        app.selectbox(key="reagendar-consulta-" + filtro).select(9 if filtro == "profissional" else 2).run()
    assert not app.exception
    assert "chamadas_mutacao" not in app.session_state
    if filtro != "paciente":
        assert app.selectbox(key="reagendar-consulta-horario").value is None
    else:
        assert app.selectbox(key="reagendar-consulta-consulta").value is None


@pytest.mark.parametrize("falha,mensagem", [
    ("sem_opcoes", "Cadastre Pacientes"), ("sem_consultas", "Nenhuma Consulta"),
    ("sem_horarios", "Nenhum horário"),
])
def test_listas_vazias_nao_permitem_envio(falha, mensagem):
    app = _abrir(falha=falha)
    if falha != "sem_opcoes":
        app.selectbox(key="reagendar-consulta-paciente").select(1).run()
    if falha == "sem_horarios":
        app.selectbox(key="reagendar-consulta-consulta").select(10).run()
        assert next(item for item in app.button if item.label == "Reagendar consulta").disabled
    assert not app.exception
    assert any(mensagem in item.value for item in app.info)
    assert "chamadas_mutacao" not in app.session_state


def test_falha_de_leitura_exibe_mensagem_segura_e_atualizar_recarrega():
    app = _abrir(falha="consultas_503")
    app.selectbox(key="reagendar-consulta-paciente").select(1).run()
    assert any("Não foi possível" in item.value for item in app.error)
    assert not any("secreto" in item.value for item in app.error)
    app.button(key="reagendar-consulta-atualizar").click().run()
    assert not app.exception
    assert app.selectbox(key="reagendar-consulta-paciente").value is None


def test_cancelar_volta_para_agenda_sem_mutacao():
    app = _selecionar_consulta(_abrir())
    next(item for item in app.button if item.label == "Cancelar").click().run()
    assert app.session_state["pagina_equipe"] == "agenda"
    assert "chamadas_mutacao" not in app.session_state
