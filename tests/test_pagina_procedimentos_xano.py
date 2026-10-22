from datetime import datetime, timedelta, timezone
from unittest.mock import Mock

import pytest
from streamlit.testing.v1 import AppTest

from sorrisomais.api import ClienteXano, ContaAcesso, Credencial


def abrir_catalogo(monkeypatch, perfil="administrador", resposta=None, erro=None, sessao_presente=True):
    monkeypatch.setenv("XANO_API_BASE_URL", "https://exemplo.invalid/api:teste")
    monkeypatch.setenv("SORRISOMAIS_MODO_DEMONSTRACAO", "1")
    validade = datetime.now(timezone.utc) + timedelta(hours=1)
    conta = ContaAcesso(1, "Conta Fictícia", (perfil,), validade)
    monkeypatch.setattr(ClienteXano, "entrar", Mock(return_value=Credencial("token-ficticio", validade)))
    monkeypatch.setattr(ClienteXano, "identificar", Mock(return_value=conta))
    lista = Mock(side_effect=erro if erro else None, return_value=resposta or {"procedimentos": []})
    monkeypatch.setattr(ClienteXano, "listar_opcoes_agenda", lista)
    codigo = """
from sorrisomais.api import ClienteXano, ContaAcesso
from sorrisomais.config import Configuracao
from sorrisomais.pagina_procedimentos_xano import renderizar
from sorrisomais import sessao
from datetime import datetime, timezone
import streamlit as st
conta = ContaAcesso(1, 'Conta Fictícia', ('PERFIL_TESTE',), datetime.now(timezone.utc))
if SESSION_PRESENTE:
    token = st.session_state.get('token_teste', 'token-ficticio')
    st.session_state[sessao.CHAVE] = type('Sessao', (), {'token': token})()
renderizar(ClienteXano(Configuracao.do_ambiente()), conta)
""".replace("PERFIL_TESTE", perfil).replace("SESSION_PRESENTE", repr(sessao_presente))
    app = AppTest.from_string(codigo, default_timeout=20).run()
    return app, lista


def test_catalogo_exibe_somente_nomes_recebidos_do_xano(monkeypatch):
    app, lista = abrir_catalogo(monkeypatch, resposta={"procedimentos": [
        {"id": 1, "nome": "Avaliação fictícia"}, {"id": 2, "nome": "Limpeza"},
    ]})
    assert not app.exception
    assert lista.call_args.args == ("token-ficticio",)
    assert any("Avaliação fictícia" in item.value for item in app.markdown)
    assert any("Limpeza" in item.value for item in app.markdown)
    assert not any("R$" in item.value or "min" in item.value for item in app.markdown)


def test_catalogo_informa_lista_vazia(monkeypatch):
    app, lista = abrir_catalogo(monkeypatch)
    assert not app.exception
    assert any("Nenhum Procedimento disponível" in item.value for item in app.info)
    lista.assert_called_once_with("token-ficticio")


def test_catalogo_trata_falha_e_oferece_tentativa(monkeypatch):
    from sorrisomais.api import ErroAcesso
    app, _ = abrir_catalogo(monkeypatch, erro=ErroAcesso("Falha", 503))
    assert not app.exception
    assert any("Não foi possível carregar" in item.value for item in app.error)
    assert any(botao.label == "Tentar novamente" for botao in app.button)


@pytest.mark.parametrize("perfil", ["profissional", "recepcionista"])
def test_perfil_sem_acesso_nao_carrega_opcoes(monkeypatch, perfil):
    app, lista = abrir_catalogo(monkeypatch, perfil=perfil)
    assert not app.exception
    assert any("não tem acesso" in item.value for item in app.info)
    lista.assert_not_called()


@pytest.mark.parametrize("status", [401, 403])
def test_sessao_e_limpa_quando_xano_nega_acesso(monkeypatch, status):
    from sorrisomais import sessao
    from sorrisomais.api import ErroAcesso
    app, _ = abrir_catalogo(monkeypatch, erro=ErroAcesso("Acesso negado. Entre novamente.", status))
    assert not app.exception
    assert app.session_state.get(sessao.CHAVE) is None
    assert any("Acesso negado" in item.value for item in app.error)


def test_sessao_ausente_mostra_mensagem_segura_sem_chamar_xano(monkeypatch):
    app, lista = abrir_catalogo(monkeypatch, sessao_presente=False)
    assert not app.exception
    assert any("Sua sessão expirou" in item.value for item in app.info)
    lista.assert_not_called()


def test_busca_nao_repete_get_enquanto_mesma_sessao_esta_ativa(monkeypatch):
    app, lista = abrir_catalogo(monkeypatch, resposta={"procedimentos": [
        {"id": 1, "nome": "Avaliação"}, {"id": 2, "nome": "Limpeza"},
    ]})
    assert not app.exception
    assert lista.call_count == 1

    app.text_input[0].set_value("limp").run()

    assert not app.exception
    lista.assert_called_once_with("token-ficticio")
    assert any("Limpeza" in item.value for item in app.markdown)
    assert not any("Avaliação" in item.value for item in app.markdown)


def test_catalogo_atualiza_apos_ttl_de_vinte_segundos(monkeypatch):
    from sorrisomais import pagina_procedimentos_xano

    relogio = {"agora": 100.0}
    monkeypatch.setattr(pagina_procedimentos_xano, "monotonic", lambda: relogio["agora"])
    app, lista = abrir_catalogo(monkeypatch, resposta={"procedimentos": [
        {"id": 1, "nome": "Limpeza"},
    ]})
    assert lista.call_count == 1

    relogio["agora"] = 119.99
    app.run()
    assert lista.call_count == 1

    relogio["agora"] = 120.0
    app.run()
    assert not app.exception
    assert lista.call_count == 2


def test_botao_atualizar_limpa_cache_e_carrega_novamente(monkeypatch):
    app, lista = abrir_catalogo(monkeypatch, resposta={"procedimentos": [
        {"id": 1, "nome": "Limpeza"},
    ]})
    assert lista.call_count == 1
    assert any(botao.label == "Atualizar catálogo" for botao in app.button)

    app.button[0].click().run()

    assert not app.exception
    assert lista.call_count == 2


def test_falha_nao_repete_get_ate_tentativa_manual(monkeypatch):
    from sorrisomais.api import ErroAcesso

    falha = ErroAcesso("Falha temporária", 503)
    resposta = {"procedimentos": [{"id": 1, "nome": "Limpeza"}]}
    app, lista = abrir_catalogo(monkeypatch, erro=[falha, resposta], resposta=resposta)
    assert not app.exception
    assert lista.call_count == 1

    app.button[0].click().run()

    assert not app.exception
    assert lista.call_count == 2
    assert any("Limpeza" in item.value for item in app.markdown)


def test_cache_de_catalogo_e_invalido_ao_trocar_token(monkeypatch):
    app, lista = abrir_catalogo(monkeypatch, resposta={"procedimentos": [
        {"id": 1, "nome": "Limpeza"},
    ]})
    assert lista.call_count == 1
    app.session_state["token_teste"] = "token-novo"
    app.run()

    assert not app.exception
    assert lista.call_count == 2
    assert lista.call_args.args == ("token-novo",)
