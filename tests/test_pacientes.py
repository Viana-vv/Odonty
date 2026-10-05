"""Contrato e interface com dados sintéticos; não substituem testes no Xano."""

from datetime import date, timedelta
from uuid import uuid4
from unittest.mock import Mock

import pytest
import requests

from sorrisomais import sessao
from sorrisomais.api import ClienteXano, ContaAcesso, ErroAcesso
from sorrisomais.pacientes import hoje, validar_cadastro
from test_profissionais import api, http, resposta, cliente, abrir_admin, botao


DADOS = dict(nome="Paciente Fictício", data_nascimento="2000-02-29", telefone="11900000000", cpf="98700000027", email="ficticio@example.com", celular="11911112222")


def payload(**alteracoes):
    return dict(DADOS, operacao_id=str(uuid4()), **alteracoes)


def test_todos_os_campos_obrigatorios_e_normalizacao():
    dados = validar_cadastro(" Paciente Fictício ", "2000-02-29", "(11) 90000-0000",
                              "987.000.000-27", " FICTICIO@EXAMPLE.COM ", "(11) 91111-2222")
    assert dados == dict(DADOS, nome="Paciente Fictício", telefone="11900000000",
                         cpf="98700000027", email="ficticio@example.com", celular="11911112222")


@pytest.mark.parametrize("campo", ["nome", "data_nascimento", "telefone", "cpf", "email", "celular"])
def test_todos_os_campos_sao_obrigatorios(campo):
    dados = dict(DADOS, **{campo: " "})
    with pytest.raises(ErroAcesso, match="Preencha"):
        validar_cadastro(**dados)


@pytest.mark.parametrize("campo,valor", [
    ("nome", ""), ("nome", "   "), ("nome", None), ("nome", True),
    ("nome", "a"), ("nome", "a" * 121),
    ("data_nascimento", ""), ("data_nascimento", None), ("data_nascimento", True),
    ("data_nascimento", "2001-02-29"), ("data_nascimento", "2000-2-29"),
    ("data_nascimento", "0000-01-01"), ("data_nascimento", "2000-01-01T00:00:00"),
    ("cpf", "11111111111"), ("cpf", "00000000000"), ("cpf", "123"), ("cpf", True),
    ("cpf", "１２３４５６７８９０１"), ("cpf", "123 456 789 01"),
    ("email", "invalido"), ("email", "a b@example.com"), ("email", "x" * 255),
    ("celular", "123"), ("celular", "+5511900000000"), ("celular", True),
    ("celular", "１１９００００００００"),
])
def test_dados_invalidos_nao_enviam(http, campo, valor):
    dados = dict(payload(), **{campo: valor})
    with pytest.raises(ErroAcesso) as erro:
        cliente().cadastrar_paciente("token-ficticio", **dados)
    assert erro.value.status == 400
    http.assert_not_called()


def test_limites_e_nascimento_futuro():
    validar_cadastro(**dict(DADOS, nome="ab", data_nascimento="0001-01-01"))
    validar_cadastro(**dict(DADOS, nome="a" * 120, data_nascimento=hoje().isoformat()))
    with pytest.raises(ErroAcesso, match="futuro"):
        validar_cadastro(**dict(DADOS, data_nascimento=(hoje() + timedelta(days=1)).isoformat()))


def test_cpf_sintetico_com_verificadores():
    # Sequência artificial; não representa identidade de pessoa real.
    numeros = [9, 8, 7, 0, 0, 0, 0, 0, 0]
    for tamanho in (9, 10):
        resto = sum(n * p for n, p in zip(numeros, range(tamanho + 1, 1, -1))) % 11
        numeros.append(0 if resto < 2 else 11 - resto)
    cpf = "".join(map(str, numeros))
    mascara = f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
    assert validar_cadastro(**dict(DADOS, cpf=mascara))["cpf"] == cpf
    with pytest.raises(ErroAcesso):
        validar_cadastro(**dict(DADOS, cpf=cpf[:-1] + str((numeros[-1] + 1) % 10)))


@pytest.mark.parametrize("token", [None, "", " ", True, "token\n"])
def test_sem_login_nao_envia(http, token):
    with pytest.raises(ErroAcesso) as erro:
        cliente().cadastrar_paciente(token, **payload())
    assert erro.value.status == 401
    http.assert_not_called()


@pytest.mark.parametrize("operacao", [None, "", True, "nao-uuid", "00000000-0000-0000-0000-000000000000"])
def test_operacao_obrigatoria(http, operacao):
    with pytest.raises(ErroAcesso):
        cliente().cadastrar_paciente("token", **dict(payload(), operacao_id=operacao))
    http.assert_not_called()


def test_contrato_sucesso(http):
    dados = payload()
    resposta(http, {"paciente": {"id": 12, "nome": DADOS["nome"], "situacao": "ativo"},
                    "operacao_id": dados["operacao_id"]}, 201)
    assert cliente().cadastrar_paciente("token", **dados) == 12
    http.assert_called_once()
    assert http.call_args.kwargs["json"] == dict(dados)
    assert http.call_args.kwargs["headers"]["Authorization"] == "Bearer token"


def test_resposta_de_outra_operacao_nao_confirma(http):
    resposta(http, {"paciente": {"id": 12, "nome": DADOS["nome"], "situacao": "ativo"},
                    "operacao_id": str(uuid4())}, 201)
    with pytest.raises(ErroAcesso, match="confirmar"):
        cliente().cadastrar_paciente("token", **payload())


def test_json_invalido_nao_confirma(http):
    retorno = resposta(http, {}, 201)
    retorno.json.side_effect = ValueError("SEGREDO")
    with pytest.raises(ErroAcesso, match="confirmar"):
        cliente().cadastrar_paciente("token", **payload())


@pytest.mark.parametrize("status,codigo", [(400, None), (401, None), (403, None),
    (409, "CPF_DUPLICADO"), (409, "OPERACAO_CONFLITANTE"), (429, None), (503, None)])
def test_erros_seguros(http, status, codigo):
    resposta(http, {"codigo": codigo, "mensagem": "SEGREDO"}, status)
    with pytest.raises(ErroAcesso) as erro:
        cliente().cadastrar_paciente("token", **payload())
    assert erro.value.status == status
    assert erro.value.codigo == codigo
    assert "SEGREDO" not in str(erro.value)
    assert "CRO" not in str(erro.value)
    http.assert_called_once()


@pytest.mark.parametrize("corpo", [{}, {"codigo": "SEGREDO"}, {"codigo": []}, None])
def test_conflito_desconhecido_e_incerto(http, corpo):
    resposta(http, corpo, 409)
    with pytest.raises(ErroAcesso, match="confirmar"):
        cliente().cadastrar_paciente("token", **payload())


@pytest.mark.parametrize("falha", [requests.Timeout, requests.ConnectionError])
def test_falha_sem_repeticao(http, falha):
    http.side_effect = falha("SEGREDO")
    with pytest.raises(ErroAcesso, match="confirmar"):
        cliente().cadastrar_paciente("token", **payload())
    http.assert_called_once()


@pytest.mark.parametrize("alteracao", [{"id": True}, {"id": 0}, {"nome": "Outro"}, {"situacao": "inativo"}])
def test_resposta_incompativel(http, alteracao):
    dados = payload()
    resposta(http, {"paciente": dict(id=12, nome=DADOS["nome"], situacao="ativo") | alteracao,
                    "operacao_id": dados["operacao_id"]}, 201)
    with pytest.raises(ErroAcesso, match="confirmar"):
        cliente().cadastrar_paciente("token", **dados)


@pytest.fixture
def paciente_api(api, monkeypatch):
    monkeypatch.setenv("XANO_CADASTRO_PACIENTE_HABILITADO", "1")
    cadastrar = Mock(return_value=12)
    monkeypatch.setattr(ClienteXano, "cadastrar_paciente", cadastrar)
    api["cadastrar_paciente"] = cadastrar
    return api


def formulario(api):
    app = abrir_admin(api)
    botao(app, "Cadastrar paciente").click().run()
    assert not app.exception
    return app


def preencher(app):
    app.text_input(key="pac_nome").set_value(DADOS["nome"])
    app.date_input(key="pac_data_nascimento").set_value(date(2000, 2, 29))
    for campo in ("telefone", "celular"):
        app.number_input(key="pac_" + campo).set_value(int(DADOS[campo]))
    for campo in ("cpf", "email"):
        app.text_input(key="pac_" + campo).set_value(DADOS[campo])


def test_vazios_nao_enviam(paciente_api):
    app = formulario(paciente_api)
    botao(app, "Cadastrar").click().run()
    assert not app.exception
    assert app.error
    paciente_api["cadastrar_paciente"].assert_not_called()
    app.text_input(key="pac_nome").set_value(DADOS["nome"])
    botao(app, "Cadastrar").click().run()
    assert app.error
    paciente_api["cadastrar_paciente"].assert_not_called()


def test_sucesso_limpa_preserva_equipe(paciente_api):
    app = formulario(paciente_api)
    operacao = app.session_state["pac_operacao_id"]
    preencher(app)
    botao(app, "Cadastrar").click().run()
    assert not app.exception
    paciente_api["cadastrar_paciente"].assert_called_once()
    assert app.success
    assert app.text_input(key="pac_nome").value == ""
    assert app.date_input(key="pac_data_nascimento").value is None
    assert app.number_input(key="pac_telefone").value is None
    assert app.text_input(key="pac_cpf").value == ""
    assert app.text_input(key="pac_email").value == ""
    assert app.number_input(key="pac_celular").value is None
    assert app.session_state["pac_operacao_id"] != operacao
    assert app.session_state[sessao.CHAVE].token == "token-adm"


@pytest.mark.parametrize("erro", [ErroAcesso("Corrija", 400), ErroAcesso("Duplicado", 409, "CPF_DUPLICADO")])
def test_rejeicao_preserva_e_renova_chave(paciente_api, erro):
    paciente_api["cadastrar_paciente"].side_effect = [erro, 12]
    app = formulario(paciente_api)
    operacao = app.session_state["pac_operacao_id"]
    preencher(app)
    botao(app, "Cadastrar").click().run()
    assert not app.exception
    assert app.text_input(key="pac_nome").value == DADOS["nome"]
    assert app.date_input(key="pac_data_nascimento").value == date(2000, 2, 29)
    assert app.session_state["pac_operacao_id"] != operacao
    botao(app, "Cadastrar").click().run()
    assert app.success


@pytest.mark.parametrize("status", [None, 429, 503])
def test_incerto_reenvia_mesma_operacao(paciente_api, status):
    chamada = paciente_api["cadastrar_paciente"]
    chamada.side_effect = [ErroAcesso("Sem confirmação", status), 12]
    app = formulario(paciente_api)
    preencher(app)
    botao(app, "Cadastrar").click().run()
    assert not app.exception
    assert app.text_input(key="pac_nome").disabled
    assert botao(app, "Cadastrar").disabled
    app.run()
    chamada.assert_called_once()
    botao(app, "Reenviar mesma operação").click().run()
    assert not app.exception
    assert app.success
    assert chamada.call_args_list[0] == chamada.call_args_list[1]


@pytest.mark.parametrize("perfil", ["administrador", "recepcionista", "profissional"])
def test_permissoes_e_navegacao_adulterada(paciente_api, perfil):
    atual = paciente_api["identificar"].return_value
    paciente_api["identificar"].return_value = ContaAcesso(1, atual.nome, (perfil,), atual.expira_em)
    app = abrir_admin(paciente_api)
    labels = [b.label for b in app.button]
    assert ("Cadastrar profissional" in labels) == (perfil == "administrador")
    assert ("Cadastrar paciente" in labels) == (perfil != "profissional")
    app.session_state["pagina_equipe"] = "paciente"
    app.session_state["pac_nome"] = "Paciente Fictício"
    app.run()
    assert not app.exception
    if perfil == "profissional":
        assert "pac_nome" not in app.session_state
        assert not app.date_input


@pytest.mark.parametrize("acao", ["Voltar", "Sair", "perda_perfil", "expiracao", "falha_revalidacao"])
def test_saida_limpa_dados(paciente_api, acao):
    app = formulario(paciente_api)
    preencher(app)
    botao(app, "Cadastrar").click().run()
    app.session_state["pac_nome"] = "Paciente Fictício"
    app.session_state["pac_pendente"] = payload()
    if acao == "perda_perfil":
        atual = paciente_api["identificar"].return_value
        paciente_api["identificar"].return_value = ContaAcesso(1, atual.nome, ("profissional",), atual.expira_em)
        app.session_state[sessao.CHAVE_VERIFICADA] -= timedelta(
            seconds=sessao.INTERVALO_REVALIDACAO_SEGUNDOS + 1)
        app.run()
    elif acao in ("expiracao", "falha_revalidacao"):
        paciente_api["identificar"].side_effect = ErroAcesso("Sessão indisponível", 401 if acao == "expiracao" else 503)
        app.session_state[sessao.CHAVE_VERIFICADA] -= timedelta(
            seconds=sessao.INTERVALO_REVALIDACAO_SEGUNDOS + 1)
        app.run()
    else:
        botao(app, acao).click().run()
    assert not app.exception
    assert not any(k.startswith("pac_") for k in app.session_state)


@pytest.mark.parametrize("status", [401, 403])
def test_perda_acesso_durante_envio(paciente_api, status):
    paciente_api["cadastrar_paciente"].side_effect = ErroAcesso("Acesso negado", status)
    app = formulario(paciente_api)
    preencher(app)
    botao(app, "Cadastrar").click().run()
    assert not app.exception
    assert sessao.CHAVE not in app.session_state
    assert not any(k.startswith("pac_") for k in app.session_state)


def test_interface_pode_ser_desabilitada_explicitamente(paciente_api, monkeypatch):
    monkeypatch.setenv("XANO_CADASTRO_PACIENTE_HABILITADO", "0")
    app = abrir_admin(paciente_api)
    assert "Cadastrar paciente" not in [b.label for b in app.button]
    app.session_state["pagina_equipe"] = "paciente"
    app.run()
    assert not app.date_input


def test_interface_disponivel_sem_variavel(paciente_api, monkeypatch):
    monkeypatch.delenv("XANO_CADASTRO_PACIENTE_HABILITADO", raising=False)
    app = abrir_admin(paciente_api)
    assert "Cadastrar paciente" in [b.label for b in app.button]
    botao(app, "Cadastrar paciente").click().run()
    assert [campo.label for campo in app.text_input if campo.key.startswith("pac_")]


def test_campos_de_telefone_limitam_tamanho_no_formulario(paciente_api):
    app = formulario(paciente_api)
    assert app.text_input(key="pac_telefone").max_chars == 15
    assert app.text_input(key="pac_celular").max_chars == 15
def test_campos_de_telefone_aceitam_somente_numeros_nacionais(paciente_api):
    app = formulario(paciente_api)
    for campo in ("pac_telefone", "pac_celular"):
        widget = app.number_input(key=campo)
        assert widget.min == 0
        assert widget.max == 99_999_999_999
        assert widget.step == 1


def test_multiplos_perfis(paciente_api):
    atual = paciente_api["identificar"].return_value
    paciente_api["identificar"].return_value = ContaAcesso(
        1, atual.nome, ("profissional", "recepcionista"), atual.expira_em)
    app = formulario(paciente_api)
    preencher(app)
    botao(app, "Cadastrar").click().run()
    assert app.success


def test_conflito_operacao_nao_permite_novo_envio(paciente_api):
    chamada = paciente_api["cadastrar_paciente"]
    chamada.side_effect = ErroAcesso("Conflito", 409, "OPERACAO_CONFLITANTE")
    app = formulario(paciente_api)
    preencher(app)
    botao(app, "Cadastrar").click().run()
    assert not app.exception
    assert botao(app, "Reenviar mesma operação").disabled
    assert botao(app, "Cadastrar").disabled
    assert not botao(app, "Voltar").disabled
    app.run()
    chamada.assert_called_once()


def test_callback_duplo_nao_sobrescreve_operacao(monkeypatch):
    from sorrisomais import pagina_paciente
    estado = dict(pac_nome=DADOS["nome"], pac_data_nascimento=date(2000, 2, 29),
                  pac_telefone=DADOS["telefone"], pac_cpf=DADOS["cpf"],
                  pac_email=DADOS["email"], pac_celular=DADOS["celular"])
    monkeypatch.setattr(pagina_paciente.st, "session_state", estado)
    pagina_paciente.solicitar()
    primeira = dict(estado["pac_pendente"])
    estado["pac_nome"] = "Outro Paciente Fictício"
    pagina_paciente.solicitar()
    assert estado["pac_pendente"] == primeira
