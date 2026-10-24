from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import Mock

import streamlit as st
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


def test_administrador_autorizado_visualiza_conta_e_carregamento(monkeypatch):
    cliente = cliente_mock()
    carregando = []

    @contextmanager
    def spinner(mensagem):
        carregando.append(mensagem)
        yield

    monkeypatch.setattr(st, "spinner", spinner)
    app = abrir(cliente)

    assert not app.exception
    assert any(item.value == "Contas de Acesso" for item in app.title)
    assert "Ana Administradora Fictícia" in texto(app)
    assert "ana@example.invalid" in texto(app)
    assert "Perfis: Administrador" in texto(app)
    assert "Ativo" in texto(app)
    assert [botao.label for botao in app.button] == ["Atualizar lista"]
    assert carregando == ["Carregando Contas de Acesso…"]
    cliente._request.assert_called_once_with("GET", "/contas-acesso", token="token-ficticio")


def test_perfil_profissional_e_exibido_com_nome_do_dominio():
    cliente = cliente_mock()
    cliente._request.return_value = {"contas_acesso": [conta_ficticia(perfis=["profissional"])]}
    app = abrir(cliente, perfis=("recepcionista",))

    assert not app.exception
    assert "Perfis: Profissional" in texto(app)
    assert "Dentista" not in texto(app)


def test_botao_atualizar_refaz_consulta():
    cliente = cliente_mock()
    app = abrir(cliente)

    app.button(key="contas-acesso-atualizar").click().run()

    assert not app.exception
    assert cliente._request.call_count == 2


def test_ordem_dos_cartoes_permanece_sequencial_ao_empilhar_linhas():
    cliente = cliente_mock()
    cliente._request.return_value = {"contas_acesso": [
        conta_ficticia(id=identificador, nome=f"Conta Fictícia {identificador}")
        for identificador in range(1, 7)
    ]}

    app = abrir(cliente)

    assert not app.exception
    assert [item.value for item in app.subheader] == [
        f"Conta Fictícia {identificador}" for identificador in range(1, 7)
    ]


def test_perfil_sem_permissao_nao_consulta_api():
    cliente = cliente_mock()
    app = abrir(cliente, perfis=("profissional",))

    assert not app.exception
    assert any("não tem permissão" in item.value for item in app.info)
    assert not app.button
    cliente._request.assert_not_called()


def test_lista_vazia_exibe_estado_informativo():
    cliente = cliente_mock()
    cliente._request.return_value = {"contas_acesso": []}
    app = abrir(cliente)

    assert not app.exception
    assert any("Não há Contas de Acesso" in item.value for item in app.info)


def test_falha_api_exibe_mensagem_segura():
    cliente = cliente_mock()
    cliente._request.side_effect = [
        ErroAcesso("mensagem técnica com token", 503),
        {"contas_acesso": [conta_ficticia()]},
    ]
    app = abrir(cliente)

    assert not app.exception
    assert any("Não foi possível carregar" in item.value for item in app.error)
    assert all("token" not in item.value for item in app.error)

    app.button(key="contas-acesso-atualizar").click().run()

    assert not app.exception
    assert "Ana Administradora Fictícia" in texto(app)


def test_acesso_negado_pelo_xano_mostra_mensagem_segura():
    cliente = cliente_mock()
    cliente._request.side_effect = ErroAcesso("resposta técnica", 403)
    app = abrir(cliente)

    assert not app.exception
    assert any("não tem permissão" in item.value for item in app.error)
    assert all("resposta técnica" not in item.value for item in app.error)


def test_sessao_expirada_e_limpa_sem_expor_detalhes_da_api():
    cliente = cliente_mock()
    cliente._request.side_effect = ErroAcesso("token vencido", 401)
    app = abrir(cliente)

    assert not app.exception
    assert any("Sua sessão expirou" in item.value for item in app.error)
    assert all("token vencido" not in item.value for item in app.error)
    assert sessao.CHAVE not in app.session_state
    assert not app.button
