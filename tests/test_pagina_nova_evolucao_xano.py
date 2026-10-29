"""Testes da tela de nova evolução sem chamadas de rede."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest


CONSULTAS = [
    {"id": 17, "paciente_id": 3, "paciente_nome": "Paciente Fictícia", "profissional_id": 9,
     "profissional_nome": "Dra. Fictícia", "inicio_em": "2026-10-10T10:00:00Z", "situacao": "Realizada"},
    {"id": 18, "paciente_id": 4, "paciente_nome": "Paciente Fictício Bruno", "profissional_id": 9,
     "profissional_nome": "Dra. Fictícia", "inicio_em": "2026-10-11T10:00:00Z", "situacao": "Realizada"},
]


def abrir(*, perfis=("profissional",), falha=None, paciente_selecionado=None):
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
if "_iniciado" not in st.session_state:
    st.session_state["_iniciado"] = True
    st.session_state["credencial"] = Credencial("token-ficticio", datetime.now(timezone.utc) + timedelta(hours=1))
    st.session_state[pagina._CHAVE_ABERTO] = True
    st.session_state["prontuario_paciente_id"] = {paciente_selecionado!r}
class ClienteFalso:
    def registrar_clinico(self, token, paciente_id, conteudo, *, consulta_id=None):
        st.session_state["_envios"] = st.session_state.get("_envios", 0) + 1
        st.session_state["_registro_enviado"] = {{"paciente_id": paciente_id, "conteudo": conteudo, "consulta_id": consulta_id}}
        {f'raise ErroAcesso("Falha segura.", {falha})' if falha else 'return {"id": 42}'}
renderizar(ClienteFalso(), SimpleNamespace(nome="Dra. Fictícia", perfis={perfis!r}), {CONSULTAS!r})
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
    assert "nova-evolucao-conteudo" not in app.session_state
    assert "prontuario_nova_evolucao_aberta" not in app.session_state
    assert not app.text_area


def test_abertura_respeita_paciente_filtrado_no_prontuario():
    app = abrir(paciente_selecionado=4)
    assert not app.exception
    assert app.selectbox(key="nova-evolucao-paciente").value == 4
    assert all("2026-10-10" not in opcao for opcao in app.selectbox(key="nova-evolucao-consulta").options)


def test_troca_de_paciente_atualiza_consultas_e_descarta_conteudo_anterior():
    app = abrir()
    assert not app.selectbox(key="nova-evolucao-paciente").form_id
    app.text_area[0].set_value("Evolução fictícia do primeiro Paciente")
    app.selectbox(key="nova-evolucao-consulta").set_value(17)
    app.selectbox(key="nova-evolucao-paciente").set_value(4).run()
    assert not app.exception
    assert app.text_area[0].value == ""
    assert app.selectbox(key="nova-evolucao-consulta").value is None
    app.selectbox(key="nova-evolucao-consulta").set_value(18)
    app.text_area[0].set_value("Evolução fictícia de Bruno")
    next(botao for botao in app.button if botao.label == "Salvar no prontuário").click().run()
    assert not app.exception
    assert app.session_state["_registro_enviado"] == {
        "paciente_id": 4, "consulta_id": 18, "conteudo": "Evolução fictícia de Bruno",
    }


@pytest.mark.parametrize("acao", ["nova-evolucao-cancelar", "nova-evolucao-fechar"])
def test_cancelar_ou_fechar_descarta_rascunho_sem_chamar_api(acao):
    app = abrir()
    app.text_area[0].set_value("Rascunho fictício descartado")
    app.button(key=acao).click().run()
    assert not app.exception
    assert "_registro_enviado" not in app.session_state
    assert not app.text_area
    app.button(key="prontuario-nova-evolucao").click().run()
    assert not app.exception
    assert app.text_area[0].value == ""


def test_sucesso_fecha_formulario_e_nova_abertura_nao_reenvia_conteudo():
    app = abrir()
    app.text_area[0].set_value("Evolução fictícia confirmada")
    next(botao for botao in app.button if botao.label == "Salvar no prontuário").click().run()
    assert not app.exception
    assert not app.text_area
    app.button(key="prontuario-nova-evolucao").click().run()
    assert not app.exception
    assert app.text_area[0].value == ""
    assert app.session_state["_envios"] == 1


def test_encerrar_sessao_remove_rascunho_e_contexto_clinico():
    from sorrisomais import sessao

    estado = {
        "nova-evolucao-conteudo": "Rascunho fictício",
        "nova-evolucao-paciente": 3,
        "nova-evolucao-consulta": 17,
        "prontuario_nova_evolucao_aberta": True,
        "prontuario_paciente_pendente": 3,
        "prontuario_aviso": "Confirmação fictícia",
        "preferencia_nao_relacionada": "preservar",
    }
    sessao.limpar(estado)
    assert estado == {"preferencia_nao_relacionada": "preservar"}


@pytest.mark.parametrize("status", [403, 404, 429, 503])
def test_falha_preserva_texto_e_nao_repete_post_em_rerun(status):
    app = abrir(falha=status)
    app.text_area[0].set_value("Evolução fictícia preservada")
    next(botao for botao in app.button if botao.label == "Salvar no prontuário").click().run()
    assert not app.exception
    assert app.text_area[0].value == "Evolução fictícia preservada"
    assert not app.success
    app.run()
    assert app.session_state["_envios"] == 1
