from datetime import datetime, timedelta, timezone
from unittest.mock import Mock

import pytest
from streamlit.testing.v1 import AppTest

from sorrisomais.api import ClienteXano, ContaAcesso, Credencial


def abrir_catalogo(monkeypatch, perfil="administrador", resposta=None, erro=None):
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
st.session_state[sessao.CHAVE] = type('Sessao', (), {'token': 'token-ficticio'})()
renderizar(ClienteXano(Configuracao.do_ambiente()), conta)
""".replace("PERFIL_TESTE", perfil)
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
