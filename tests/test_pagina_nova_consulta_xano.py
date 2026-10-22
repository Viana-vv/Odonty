"""Testes sem rede da tela Nova Consulta conectada."""
from pathlib import Path

from streamlit.testing.v1 import AppTest


def _abrir_tela(*, perfil="recepcionista", falha=None):
    falha_codigo = {
        "conflito": "raise ErroAcesso('Este horário acabou de ser reservado. Escolha outro.', 409)",
        "opcoes": "raise ErroAcesso('Aguarde alguns segundos.', 429)",
        "disponibilidades": "raise ErroAcesso('Falha de conexão.', 503)",
    }.get(falha, "return None")
    fonte = f'''
from datetime import date, timedelta
import sys
from types import SimpleNamespace
import streamlit as st
sys.path.insert(0, {str(Path(__file__).resolve().parents[1])!r})
from sorrisomais.api import ErroAcesso
from sorrisomais import sessao
from sorrisomais.pagina_nova_consulta_xano import renderizar

class ClienteFicticio:
    criadas = []
    def listar_opcoes_agenda(self, token):
        {falha_codigo if falha == "opcoes" else "return {'pacientes': [{'id': 1, 'nome': 'Paciente Fictício'}], 'profissionais': [{'id': 2, 'nome': 'Profissional Fictício'}], 'procedimentos': [{'id': 3, 'nome': 'Avaliação'}]}"}
    def listar_disponibilidades(self, token, profissional_id, inicio, fim):
        {falha_codigo if falha == "disponibilidades" else "return [{'id': 4, 'situacao': 'disponivel', 'inicio': (date.today() + timedelta(days=1)).isoformat() + 'T13:00:00-03:00', 'fim': (date.today() + timedelta(days=1)).isoformat() + 'T13:30:00-03:00'}]"}
    def agendar_consulta(self, token, paciente_id, disponibilidade_id, procedimento_ids, motivo=None):
        if {falha == 'conflito'}:
            {falha_codigo if falha == "conflito" else "pass"}
        self.criadas.append((paciente_id, disponibilidade_id, procedimento_ids, motivo))
        st.session_state['teste_criacao_confirmada'] = (paciente_id, disponibilidade_id, procedimento_ids, motivo)
        return {{'id': 10}}

st.session_state[sessao.CHAVE] = SimpleNamespace(token='token-ficticio')
renderizar(ClienteFicticio(), SimpleNamespace(perfis=({perfil!r},)))
'''
    return AppTest.from_string(fonte, default_timeout=10).run()


def test_recepcionista_agenda_com_contratos_existentes_sem_rede():
    app = _abrir_tela()
    assert not app.exception
    assert any(item.value == "Nova consulta" for item in app.title)
    assert app.selectbox(key="nova-consulta-paciente").options == ["Paciente Fictício"]
    assert app.selectbox(key="nova-consulta-horario").options


def test_perfil_profissional_nao_recebe_formulario_de_agendamento():
    app = _abrir_tela(perfil="profissional")
    assert not app.exception
    assert any("não tem permissão" in item.value for item in app.error)
    assert not app.selectbox


def test_conflito_xano_e_exibido_sem_confirmar_sucesso():
    app = _abrir_tela(falha="conflito")
    app.selectbox(key="nova-consulta-paciente").select(1).run()
    app.selectbox(key="nova-consulta-horario").select(4).run()
    next(button for button in app.button if button.label == "Agendar consulta").click().run()
    assert not app.exception
    assert any("acabou de ser reservado" in item.value for item in app.error)
    assert not app.success
    assert app.selectbox(key="nova-consulta-paciente").value == 1
    assert app.selectbox(key="nova-consulta-horario").value == 4


def test_agendamento_confirmado_pelo_xano_mostra_sucesso():
    app = _abrir_tela()
    app.selectbox(key="nova-consulta-paciente").select(1).run()
    app.selectbox(key="nova-consulta-horario").select(4).run()
    next(button for button in app.button if button.label == "Agendar consulta").click().run()
    assert not app.exception
    assert any(item.value == "Consulta agendada." for item in app.success)
    assert app.session_state["teste_criacao_confirmada"] == (1, 4, [], None)


def test_horario_obrigatorio_nao_envia_formulario_incompleto():
    app = _abrir_tela()
    app.selectbox(key="nova-consulta-paciente").select(1).run()
    next(button for button in app.button if button.label == "Agendar consulta").click().run()
    assert any("Selecione um horário disponível" in item.value for item in app.error)
    assert not any(item.value == "Consulta agendada." for item in app.success)


def test_paciente_obrigatorio_nao_envia_formulario_incompleto():
    app = _abrir_tela()
    next(button for button in app.button if button.label == "Agendar consulta").click().run()
    assert any("Selecione um Paciente" in item.value for item in app.error)
    assert not any(item.value == "Consulta agendada." for item in app.success)


def test_falha_ao_carregar_opcoes_interrompe_formulario():
    app = _abrir_tela(falha="opcoes")
    assert not app.exception
    assert any("Aguarde alguns segundos" in item.value for item in app.error)
    assert not app.selectbox


def test_falha_ao_carregar_disponibilidades_nao_mostra_horario():
    app = _abrir_tela(falha="disponibilidades")
    assert not app.exception
    assert any("Não foi possível carregar os horários" in item.value for item in app.error)
    assert not any(widget.key == "nova-consulta-horario" for widget in app.selectbox)
