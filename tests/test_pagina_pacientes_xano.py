"""Testes de interface da listagem conectada, sem chamadas de rede."""

from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from streamlit.testing.v1 import AppTest

from sorrisomais import pagina_pacientes_xano, sessao
from sorrisomais.api import Credencial, ErroAcesso


PACIENTES = [
    {"id": 11, "nome": "Paciente Fictícia Aurora"},
    {"id": 12, "nome": "Paciente Fictício Horizonte"},
]


def renderizar_tela(cliente, conta):
    from sorrisomais import pagina_pacientes_xano

    pagina_pacientes_xano.renderizar(cliente, conta)


@pytest.fixture
def cliente_pacientes():
    cliente = Mock()
    cliente.listar_opcoes_agenda.return_value = {
        "pacientes": [item.copy() for item in PACIENTES],
        "profissionais": [],
        "procedimentos": [],
    }
    return cliente


def abrir_tela(cliente):
    conta = SimpleNamespace(nome="Conta Fictícia", perfis=("recepcionista",))
    app = AppTest.from_function(renderizar_tela, args=(cliente, conta)).run()
    app.session_state[sessao.CHAVE] = Credencial(
        "token-ficticio",
        datetime.now(timezone.utc) + timedelta(minutes=5),
    )
    return app.run()


def test_lista_mostra_somente_id_e_nome(cliente_pacientes):
    app = abrir_tela(cliente_pacientes)

    assert not app.exception
    assert any(item.value == "Pacientes" for item in app.title)
    assert any("Paciente Fictícia Aurora" in item.value for item in app.markdown)
    assert any("Paciente Fictício Horizonte" in item.value for item in app.markdown)
    assert any(item.value == "11" for item in app.text)
    assert any(item.value == "12" for item in app.text)
    textos = [*app.markdown, *app.caption, *app.text, *app.title]
    assert not any("CPF" in item.value or "telefone" in item.value for item in textos)
    cliente_pacientes.listar_opcoes_agenda.assert_called_once_with("token-ficticio")


def test_busca_filtra_por_nome_sem_consultar_outros_campos(cliente_pacientes):
    app = abrir_tela(cliente_pacientes)
    app.text_input(key="pacientes-xano-busca").set_value("horizonte").run()

    assert any("Paciente Fictício Horizonte" in item.value for item in app.markdown)
    assert not any("Paciente Fictícia Aurora" in item.value for item in app.markdown)
    assert cliente_pacientes.listar_opcoes_agenda.call_count == 1


def test_atualizacao_manual_busca_novamente_na_api(cliente_pacientes):
    app = abrir_tela(cliente_pacientes)
    app.button(key="pacientes-xano-atualizar").click().run()

    assert cliente_pacientes.listar_opcoes_agenda.call_count == 2


def test_cache_expira_apos_vinte_segundos(cliente_pacientes, monkeypatch):
    tempo = [100.0]
    monkeypatch.setattr(pagina_pacientes_xano, "monotonic", lambda: tempo[0])
    app = abrir_tela(cliente_pacientes)

    tempo[0] += pagina_pacientes_xano.CACHE_TTL_SEGUNDOS + 1
    app.run()

    assert cliente_pacientes.listar_opcoes_agenda.call_count == 2


def test_troca_de_token_nao_reutiliza_cache_anterior(cliente_pacientes):
    app = abrir_tela(cliente_pacientes)
    app.session_state[sessao.CHAVE] = Credencial(
        "outro-token-ficticio",
        datetime.now(timezone.utc) + timedelta(minutes=5),
    )

    app.run()

    assert cliente_pacientes.listar_opcoes_agenda.call_count == 2
    assert cliente_pacientes.listar_opcoes_agenda.call_args.args == ("outro-token-ficticio",)


def test_lista_vazia_nao_insere_dados_demo(cliente_pacientes):
    cliente_pacientes.listar_opcoes_agenda.return_value["pacientes"] = []
    app = abrir_tela(cliente_pacientes)

    assert any("Nenhum Paciente disponível" in item.value for item in app.info)
    assert not any("Paciente Fictícia" in item.value or "Paciente Fictício" in item.value
                   for item in app.markdown)


def test_busca_sem_resultado_apresenta_estado_vazio(cliente_pacientes):
    app = abrir_tela(cliente_pacientes)
    app.text_input(key="pacientes-xano-busca").set_value("inexistente").run()

    assert any("Nenhum Paciente corresponde" in item.value for item in app.info)
    assert not any("Paciente Fictícia Aurora" in item.value for item in app.markdown)


def test_permissao_recusada_nao_exibe_cadastros(cliente_pacientes):
    cliente_pacientes.listar_opcoes_agenda.side_effect = ErroAcesso("erro técnico privado", 403)
    app = abrir_tela(cliente_pacientes)

    assert any("não tem permissão" in item.value for item in app.error)
    assert not any("erro técnico privado" in item.value for item in app.error)
    assert not any("Paciente Fictícia Aurora" in item.value for item in app.markdown)


def test_sessao_expirada_limpa_credencial_e_dados_cacheados(cliente_pacientes):
    cliente_pacientes.listar_opcoes_agenda.side_effect = ErroAcesso("credencial inválida", 401)
    app = abrir_tela(cliente_pacientes)

    assert any("Sua sessão expirou" in item.value for item in app.error)
    assert sessao.CHAVE not in app.session_state
    assert "pacientes_xano_cache" not in app.session_state


def test_falha_de_api_apresenta_mensagem_sem_dados(cliente_pacientes):
    cliente_pacientes.listar_opcoes_agenda.side_effect = ErroAcesso(
        "Não foi possível conectar ao serviço. Tente novamente em instantes.", 503
    )
    app = abrir_tela(cliente_pacientes)

    assert any("Não foi possível conectar ao serviço" in item.value for item in app.error)
    assert not any("Paciente Fictícia Aurora" in item.value for item in app.markdown)


def test_falha_nao_e_cacheada_e_pode_ser_tentada_novamente(cliente_pacientes):
    cliente_pacientes.listar_opcoes_agenda.side_effect = [
        ErroAcesso("Não foi possível conectar ao serviço. Tente novamente em instantes.", 503),
        {"pacientes": [item.copy() for item in PACIENTES],
         "profissionais": [], "procedimentos": []},
    ]
    app = abrir_tela(cliente_pacientes)
    assert any("Não foi possível conectar ao serviço" in item.value for item in app.error)

    app.button(key="pacientes-xano-atualizar").click().run()

    assert cliente_pacientes.listar_opcoes_agenda.call_count == 2
    assert any("Paciente Fictícia Aurora" in item.value for item in app.markdown)


def test_sessao_ausente_nao_chama_api(cliente_pacientes):
    conta = SimpleNamespace(nome="Conta Fictícia", perfis=("recepcionista",))
    app = AppTest.from_function(renderizar_tela, args=(cliente_pacientes, conta)).run()

    assert any("Sua sessão expirou" in item.value for item in app.info)
    cliente_pacientes.listar_opcoes_agenda.assert_not_called()
