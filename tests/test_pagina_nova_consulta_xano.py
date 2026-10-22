"""Testes sem rede da tela Nova Consulta conectada."""
from datetime import date, timedelta
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest


def _abrir_tela(*, perfil="recepcionista", falha=None):
    falha_codigo = {
        "conflito": "raise ErroAcesso('Este horário acabou de ser reservado. Escolha outro.', 409)",
        "opcoes": "raise ErroAcesso('Aguarde alguns segundos.', 429)",
        "opcoes_401": "raise ErroAcesso('Sua sessão expirou.', 401)",
        "opcoes_403": "raise ErroAcesso('Seu perfil não tem permissão.', 403)",
        "sem_opcoes": "return {'pacientes': [], 'profissionais': [], 'procedimentos': []}",
        "disponibilidades": "raise ErroAcesso('Falha de conexão.', 503)",
        "sem_horarios": "return []",
        "disponibilidades_401": "raise ErroAcesso('Sua sessão expirou.', 401)",
        "agendamento_401": "raise ErroAcesso('Sua sessão expirou.', 401)",
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
        {falha_codigo if falha in {"opcoes", "opcoes_401", "opcoes_403", "sem_opcoes"} else "return {'pacientes': [{'id': 1, 'nome': 'Paciente Fictício'}], 'profissionais': [{'id': 2, 'nome': 'Profissional Fictício'}], 'procedimentos': [{'id': 3, 'nome': 'Avaliação'}]}"}
    def listar_disponibilidades(self, token, profissional_id, inicio, fim):
        {falha_codigo if falha in {"disponibilidades", "disponibilidades_401", "sem_horarios"} else "dia = date.fromisoformat(inicio[:10]); identificador = 4 if dia == date.today() + timedelta(days=1) else 5; hora = '13' if identificador == 4 else '15'; return [{'id': identificador, 'situacao': 'disponivel', 'inicio': dia.isoformat() + 'T' + hora + ':00:00-03:00', 'fim': dia.isoformat() + 'T' + hora + ':30:00-03:00'}]"}
    def agendar_consulta(self, token, paciente_id, disponibilidade_id, procedimento_ids, motivo=None):
        if {falha in {'conflito', 'agendamento_401'}}:
            {falha_codigo if falha in {"conflito", "agendamento_401"} else "pass"}
        self.criadas.append((paciente_id, disponibilidade_id, procedimento_ids, motivo))
        st.session_state['teste_criacao_confirmada'] = (paciente_id, disponibilidade_id, procedimento_ids, motivo)
        return {{'id': 10}}

st.session_state[sessao.CHAVE] = SimpleNamespace(token='token-ficticio')
st.session_state[sessao.CHAVE_CONTA] = SimpleNamespace(perfis=({perfil!r},))
renderizar(ClienteFicticio(), SimpleNamespace(perfis=({perfil!r},)))
'''
    return AppTest.from_string(fonte, default_timeout=10).run()


def test_recepcionista_agenda_com_contratos_existentes_sem_rede():
    app = _abrir_tela()
    assert not app.exception
    assert any(item.value == "Nova consulta" for item in app.subheader)
    assert app.selectbox(key="nova-consulta-paciente").options == ["Paciente Fictício"]
    assert app.selectbox(key="nova-consulta-horario").options


@pytest.mark.parametrize("perfil", ["profissional", "paciente"])
def test_perfil_nao_administrativo_nao_recebe_formulario_de_agendamento(perfil):
    app = _abrir_tela(perfil=perfil)
    assert not app.exception
    assert any("não tem permissão" in item.value for item in app.error)
    assert not app.selectbox


def test_conflito_xano_e_exibido_sem_confirmar_sucesso():
    app = _abrir_tela(falha="conflito")
    app.selectbox(key="nova-consulta-paciente").select(1).run()
    app.selectbox(key="nova-consulta-horario").select(5).run()
    next(button for button in app.button if button.label == "Agendar consulta").click().run()
    assert not app.exception
    assert any("acabou de ser reservado" in item.value for item in app.error)
    assert not app.success
    assert app.selectbox(key="nova-consulta-paciente").value == 1
    assert app.selectbox(key="nova-consulta-horario").value == 5


def test_agendamento_confirmado_pelo_xano_mostra_sucesso():
    app = _abrir_tela()
    app.selectbox(key="nova-consulta-paciente").select(1).run()
    app.selectbox(key="nova-consulta-horario").select(5).run()
    next(button for button in app.button if button.label == "Agendar consulta").click().run()
    assert not app.exception
    assert any(item.value == "Consulta agendada." for item in app.success)
    assert app.session_state["teste_criacao_confirmada"] == (1, 5, [], None)


def test_horario_obrigatorio_nao_envia_formulario_incompleto():
    app = _abrir_tela()
    app.selectbox(key="nova-consulta-paciente").select(1).run()
    next(button for button in app.button if button.label == "Agendar consulta").click().run()
    assert any("Selecione um horário disponível" in item.value for item in app.error)
    assert not any(item.value == "Consulta agendada." for item in app.success)


def test_trocar_data_limpa_horario_que_nao_pertence_a_nova_data():
    app = _abrir_tela()
    amanha = date.today() + timedelta(days=1)
    depois_de_amanha = amanha + timedelta(days=1)
    app.date_input(key="nova-consulta-data").set_value(amanha).run()
    app.selectbox(key="nova-consulta-horario").select(4).run()
    assert app.selectbox(key="nova-consulta-horario").value == 4

    app.date_input(key="nova-consulta-data").set_value(depois_de_amanha).run()
    assert not app.exception
    assert app.selectbox(key="nova-consulta-horario").options == ["15:00 – 15:30"]
    assert app.selectbox(key="nova-consulta-horario").value is None


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


def test_lista_vazia_de_cadastros_exibe_instrucao():
    app = _abrir_tela(falha="sem_opcoes")
    assert not app.exception
    assert any("Cadastre Pacientes e Profissionais ativos" in item.value for item in app.info)
    assert not app.selectbox


@pytest.mark.parametrize(
    "falha",
    ["opcoes_401", "disponibilidades_401", "agendamento_401"],
)
def test_sessao_expirada_limpa_credencial_em_cada_operacao(falha):
    app = _abrir_tela(falha=falha)
    if falha == "agendamento_401":
        app.selectbox(key="nova-consulta-paciente").select(1).run()
        app.selectbox(key="nova-consulta-horario").select(5).run()
        next(button for button in app.button if button.label == "Agendar consulta").click().run()
    assert any("sessão expirou" in item.value for item in app.error)
    assert "credencial" not in app.session_state
    assert "conta_acesso_cache" not in app.session_state


def test_acesso_negado_403_mantem_credencial():
    app = _abrir_tela(falha="opcoes_403")
    assert any("não tem permissão" in item.value for item in app.error)
    assert "credencial" in app.session_state
    assert "conta_acesso_cache" in app.session_state


def test_falha_ao_carregar_disponibilidades_nao_mostra_horario():
    app = _abrir_tela(falha="disponibilidades")
    assert not app.exception
    assert any("Não foi possível carregar os horários" in item.value for item in app.error)
    assert not any(widget.key == "nova-consulta-horario" for widget in app.selectbox)


def test_lista_vazia_de_disponibilidades_desabilita_envio():
    app = _abrir_tela(falha="sem_horarios")
    assert not app.exception
    assert any("Nenhum horário disponível" in item.value for item in app.info)
    assert next(button for button in app.button if button.label == "Agendar consulta").disabled
