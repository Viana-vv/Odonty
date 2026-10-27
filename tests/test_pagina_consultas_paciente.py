"""Testes de tela do Paciente sem chamadas de rede."""

from datetime import datetime, timedelta
from unittest.mock import Mock

from streamlit.testing.v1 import AppTest

from sorrisomais.api import ErroAcesso
from sorrisomais.pagina_consultas_paciente import renderizar


def _renderizar_tela(cliente):
    from sorrisomais.pagina_consultas_paciente import renderizar
    renderizar(cliente, "token-ficticio")


def _abrir(cliente):
    return AppTest.from_function(_renderizar_tela, args=(cliente,)).run()


def test_exibe_consultas_futuras_sem_informacao_clinica():
    cliente = Mock()
    cliente.listar_consultas.return_value = [{
        "id": 1, "inicio_em": (datetime.now().astimezone() + timedelta(days=3)).isoformat(),
        "fim_em": "", "profissional_nome": "Profissional Fictício", "situacao": "Confirmada",
        "procedimentos": ["Procedimento privado"],
    }]
    app = _abrir(cliente)
    assert not app.exception
    assert any(x.value == "Minhas Consultas" for x in app.title)
    textos = [x.value for x in [*app.markdown, *app.caption]]
    assert any("Profissional Fictício" in texto for texto in textos)
    assert any("cancelamento" in texto for texto in textos)
    assert not any("Procedimento privado" in texto for texto in textos)
    cliente.listar_consultas.assert_called_once_with("token-ficticio")


def test_pode_consultar_passadas():
    cliente = Mock()
    cliente.listar_consultas.return_value = [{
        "id": 2, "inicio_em": (datetime.now().astimezone() - timedelta(days=3)).isoformat(),
        "fim_em": "", "profissional_nome": "Profissional Fictício", "situacao": "Realizada",
        "procedimentos": [],
    }]
    app = _abrir(cliente)
    app.radio(key="consultas-paciente-periodo").set_value("Passadas").run()
    assert not app.exception
    assert any(x.value == "Consultas passadas" for x in app.subheader)
    assert any("Profissional Fictício" in x.value for x in app.markdown)


def test_lista_vazia_e_falha_tem_mensagem_compreensivel():
    cliente = Mock()
    cliente.listar_consultas.return_value = []
    app = _abrir(cliente)
    assert any("não possui Consultas" in x.value for x in app.info)
    cliente.listar_consultas.side_effect = ErroAcesso("erro técnico", 503)
    app = _abrir(cliente)
    assert any("Tente novamente" in x.value for x in app.error)


def test_requisicao_nao_recebe_identificador_de_paciente():
    cliente = Mock()
    cliente.listar_consultas.return_value = []
    _abrir(cliente)
    cliente.listar_consultas.assert_called_once_with("token-ficticio")


def test_atualizar_forca_nova_leitura():
    cliente = Mock()
    cliente.listar_consultas.return_value = []
    app = AppTest.from_function(_renderizar_tela, args=(cliente,)).run()
    assert cliente.listar_consultas.call_count == 1
    app.button(key="consultas-paciente-atualizar").click().run()
    assert cliente.listar_consultas.call_count == 2
