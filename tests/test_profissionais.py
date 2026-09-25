"""Contrato e páginas do cadastro, com respostas simuladas."""
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import Mock

import pytest
import requests
from streamlit.testing.v1 import AppTest

from sorrisomais.api import ClienteXano, ContaAcesso, Credencial, ErroAcesso
from sorrisomais.config import Configuracao
from sorrisomais.profissionais import validar_cadastro
from sorrisomais import sessao

DADOS = dict(nome="Dentista Fictício", email="dentista@example.com",
             senha="senha-ficticia-segura", cro="SP-123456", especialidade_id=1)
RESULTADO = {"profissional": {"id": 10, "nome": DADOS["nome"], "cro": DADOS["cro"],
              "especialidade": {"id": 1, "nome": "Clínica geral"}, "situacao": "ativo"},
             "conta": {"id": 20, "perfis": ["profissional"], "situacao": "ativo"}}


@pytest.fixture
def http(monkeypatch):
    chamada = Mock()
    monkeypatch.setattr(requests, "request", chamada)
    return chamada


def resposta(http, dados, status=200):
    r = Mock(status_code=status)
    r.__enter__ = Mock(return_value=r)
    r.__exit__ = Mock(return_value=False)
    r.json.return_value = dados
    http.return_value = r
    return r


def cliente():
    return ClienteXano(Configuracao("https://exemplo.invalid/api:teste", 2))


def test_cadastro_contrato_normalizacao_e_senha_preservada(http):
    resposta(http, RESULTADO, 201)
    dados = dict(DADOS, nome=" Dentista Fictício ", email=" DENTISTA@example.com ",
                 cro=" sp-000123456 ", senha=" senha ficticia segura ")
    assert cliente().cadastrar_profissional("token-ficticio", **dados) == 10
    enviado = http.call_args.kwargs["json"]
    assert enviado == dict(DADOS, senha=dados["senha"])
    assert http.call_args.kwargs["headers"]["Authorization"] == "Bearer token-ficticio"
    http.assert_called_once()


@pytest.mark.parametrize("campo,valor", [
    ("nome", ""), ("nome", "A"), ("nome", "a"*121), ("nome", 1),
    ("email", "invalido"), ("email", "a"*245+"@example.com"),
    ("senha", "curta"), ("senha", "a"*129), ("senha", None),
    ("cro", "XX-1"), ("cro", "SP-0"), ("cro", "SP-12345678901"),
    ("cro", "123"), ("especialidade_id", None), ("especialidade_id", True),
    ("especialidade_id", "1"), ("especialidade_id", -1),
])
def test_invalidos_nao_chamam_api(http, campo, valor):
    with pytest.raises(ErroAcesso):
        cliente().cadastrar_profissional("t", **dict(DADOS, **{campo: valor}))
    http.assert_not_called()


@pytest.mark.parametrize("status", [400, 401, 403, 409, 429, 500, 503, 200, 302])
def test_erros_seguros_sem_repeticao(http, status):
    resposta(http, {"senha": "SEGREDO_NAO_EXIBIR"}, status)
    with pytest.raises(ErroAcesso) as erro:
        cliente().cadastrar_profissional("t", **DADOS)
    assert "SEGREDO" not in str(erro.value)
    if status in (500, 503, 200, 302):
        assert "confirmar o cadastro" in str(erro.value)
    http.assert_called_once()


@pytest.mark.parametrize("falha", [requests.Timeout, requests.ConnectionError])
def test_resultado_incerto(http, falha):
    http.side_effect = falha("SEGREDO")
    with pytest.raises(ErroAcesso, match="confirmar o cadastro"):
        cliente().cadastrar_profissional("t", **DADOS)
    http.assert_called_once()


@pytest.mark.parametrize("modificacao", [
    {"profissional": None}, {"conta": {}},
    {"profissional": dict(RESULTADO["profissional"], id=True)},
    {"profissional": dict(RESULTADO["profissional"], especialidade={"id": 2, "nome": "Outra"})},
    {"conta": dict(RESULTADO["conta"], perfis=["administrador"])},
    {"profissional": dict(RESULTADO["profissional"], nome="Outra pessoa")},
])
def test_sucesso_incompativel_nao_confirma(http, modificacao):
    resposta(http, dict(RESULTADO, **modificacao), 201)
    with pytest.raises(ErroAcesso, match="confirmar o cadastro"):
        cliente().cadastrar_profissional("t", **DADOS)


@pytest.mark.parametrize("lista", [None, {}, [{"id": True, "nome": "A"}],
                                  [{"id": 1, "nome": ""}],
                                  [{"id": 1, "nome": "A"}, {"id": 1, "nome": "B"}]])
def test_especialidades_invalidas(http, lista):
    resposta(http, {"especialidades": lista})
    with pytest.raises(ErroAcesso):
        cliente().listar_especialidades("t")


def test_especialidades_vazias(http):
    resposta(http, {"especialidades": []})
    assert cliente().listar_especialidades("t") == []


@pytest.fixture
def api(monkeypatch):
    monkeypatch.setenv("XANO_API_BASE_URL", "https://exemplo.invalid/api:teste")
    prazo = datetime.now(timezone.utc) + timedelta(hours=1)
    mocks = {
        "entrar": Mock(return_value=Credencial("token-adm", prazo)),
        "identificar": Mock(return_value=ContaAcesso(1, "Administrador Fictício", ("administrador",), prazo)),
        "sair": Mock(),
        "listar_especialidades": Mock(return_value=[{"id": 1, "nome": "Clínica geral"}]),
        "cadastrar_profissional": Mock(return_value=10),
    }
    for nome, mock in mocks.items():
        monkeypatch.setattr(ClienteXano, nome, mock)
    return mocks


def botao(app, label):
    return next(b for b in app.button if b.label == label)


def abrir_admin(api):
    app = AppTest.from_file(Path(__file__).resolve().parents[1]/"app.py", default_timeout=20).run()
    app.text_input(key="email").set_value("admin@example.com")
    app.text_input(key="senha").set_value("senha-ficticia")
    botao(app, "Entrar").click().run()
    assert not app.exception
    return app


def abrir_form(api):
    app = abrir_admin(api)
    botao(app, "Cadastrar profissional").click().run()
    assert not app.exception
    return app


def preencher(app, confirmacao=None):
    for campo in ["nome", "email", "senha", "cro"]:
        app.text_input(key="cad_"+campo).set_value(DADOS[campo])
    app.text_input(key="cad_confirmacao").set_value(confirmacao or DADOS["senha"])
    app.selectbox(key="cad_especialidade").select(1)


def test_admin_cria_sem_trocar_identidade(api):
    app = abrir_form(api)
    preencher(app)
    botao(app, "Cadastrar").click().run()
    assert not app.exception
    assert app.success
    assert app.text_input(key="cad_senha").value == ""
    assert app.text_input(key="cad_confirmacao").value == ""
    assert app.text_input(key="cad_nome").value == ""
    assert app.session_state[sessao.CHAVE].token == "token-adm"
    api["cadastrar_profissional"].assert_called_once_with("token-adm", **DADOS)


@pytest.mark.parametrize("perfil", ["profissional", "recepcionista"])
def test_outros_perfis_sem_cadastro(api, perfil):
    conta = api["identificar"].return_value
    api["identificar"].return_value = ContaAcesso(1, conta.nome, (perfil,), conta.expira_em)
    app = abrir_admin(api)
    assert all(b.label != "Cadastrar profissional" for b in app.button)
    app.session_state["pagina_equipe"] = "cadastro"
    app.run()
    assert not app.exception
    api["listar_especialidades"].assert_not_called()


def test_confirmacao_diferente_nao_envia(api):
    app = abrir_form(api)
    preencher(app, "senha-nao-confere")
    botao(app, "Cadastrar").click().run()
    assert not app.exception
    assert app.error
    assert app.text_input(key="cad_senha").value == ""
    api["cadastrar_profissional"].assert_not_called()


@pytest.mark.parametrize("status", [400, 409, 429, 503])
def test_erro_reabilita_e_limpa_senhas(api, status):
    api["cadastrar_profissional"].side_effect = ErroAcesso("Erro seguro.", status)
    app = abrir_form(api)
    preencher(app)
    botao(app, "Cadastrar").click().run()
    assert not app.exception
    assert app.error[0].value == "Erro seguro."
    assert not botao(app, "Cadastrar").disabled
    assert app.text_input(key="cad_senha").value == ""
    assert app.text_input(key="cad_confirmacao").value == ""


@pytest.mark.parametrize("status", [401, 403])
def test_perda_autorizacao_no_envio_sai(api, status):
    api["cadastrar_profissional"].side_effect = ErroAcesso("Acesso negado.", status)
    app = abrir_form(api)
    preencher(app)
    botao(app, "Cadastrar").click().run()
    assert not app.exception
    assert sessao.CHAVE not in app.session_state
    assert len(app.text_input) == 2
    assert all(k not in app.session_state for k in ("cad_senha", "cad_confirmacao", "cad_pendente"))


def test_voltar_limpa_campos(api):
    app = abrir_form(api)
    preencher(app)
    botao(app, "Voltar").click().run()
    assert not app.exception
    assert all(k not in app.session_state for k in ("cad_senha", "cad_confirmacao", "cad_pendente"))


def test_especialidades_vazias_bloqueiam(api):
    api["listar_especialidades"].return_value = []
    app = abrir_form(api)
    assert app.info
    assert botao(app, "Cadastrar").disabled


def test_falha_lista_remove_formulario(api):
    api["listar_especialidades"].side_effect = ErroAcesso(status=503)
    app = abrir_form(api)
    assert app.error
    assert len(app.text_input) == 0
    api["cadastrar_profissional"].assert_not_called()


def test_perda_perfil_apos_abrir_remove_formulario(api):
    app = abrir_form(api)
    preencher(app)
    conta = api["identificar"].return_value
    api["identificar"].return_value = ContaAcesso(1, conta.nome, ("profissional",), conta.expira_em)
    app.run()
    assert not app.exception
    assert len(app.text_input) == 0
    assert all(k not in app.session_state for k in ("cad_senha", "cad_confirmacao", "cad_pendente"))
