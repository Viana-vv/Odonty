from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import Mock

from streamlit.testing.v1 import AppTest

from sorrisomais import sessao
from sorrisomais.api import Credencial, ErroAcesso


def renderizar(cliente, conta):
    from sorrisomais import pagina_contas_acesso_xano

    pagina_contas_acesso_xano.renderizar(cliente, conta)


def abrir(cliente, perfis=("administrador",)):
    conta = SimpleNamespace(perfis=perfis)
    app = AppTest.from_function(renderizar, args=(cliente, conta))
    app.session_state[sessao.CHAVE] = Credencial(
        "token-ficticio", datetime.now(timezone.utc) + timedelta(minutes=5),
    )
    return app.run()


def conta_ficticia(**extras):
    return {
        "id": 12,
        "nome": "Ana Administradora Fictícia",
        "email": "ana@example.invalid",
        "perfis": ["administrador"],
        "situacao": "ativo",
        **extras,
    }


def cliente_mock():
    cliente = Mock()
    cliente._request.return_value = {"contas_acesso": [conta_ficticia()]}
    return cliente


def texto(app):
    grupos = (app.title, app.subheader, app.markdown, app.caption, app.text,
              app.info, app.error)
    return "\n".join(str(item.value) for grupo in grupos for item in grupo)


def test_administrador_autorizado_visualiza_conta_sem_acoes_de_escrita():
    cliente = cliente_mock()
    app = abrir(cliente)

    assert not app.exception
    assert any(item.value == "Contas de Acesso" for item in app.title)
    assert "Ana Administradora Fictícia" in texto(app)
    assert "ana@example.invalid" in texto(app)
    assert "Administrador" in texto(app)
    assert "Ativo" in texto(app)
    assert not app.button
    cliente._request.assert_called_once_with("GET", "/contas-acesso", token="token-ficticio")


def test_perfil_sem_permissao_nao_consulta_api():
    cliente = cliente_mock()
    app = abrir(cliente, perfis=("profissional",))

    assert not app.exception
    assert any("não tem permissão" in item.value for item in app.info)
    cliente._request.assert_not_called()


def test_lista_vazia_exibe_estado_informativo():
    cliente = cliente_mock()
    cliente._request.return_value = {"contas_acesso": []}
    app = abrir(cliente)

    assert not app.exception
    assert any("Não há Contas de Acesso" in item.value for item in app.info)


def test_falha_api_exibe_mensagem_segura():
    cliente = cliente_mock()
    cliente._request.side_effect = ErroAcesso("mensagem técnica com token", 503)
    app = abrir(cliente)

    assert not app.exception
    assert any("Não foi possível carregar" in item.value for item in app.error)
    assert all("token" not in item.value for item in app.error)
