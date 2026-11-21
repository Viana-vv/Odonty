from hashlib import sha256
from unittest.mock import Mock

import pytest

from sorrisomais import cadastro_recepcionista as cadastro
from sorrisomais import sessao
from sorrisomais.api import ErroAcesso
from test_roteamento_equipe_xano import abrir_app, cliente_teste, conta_teste


SENHA = "senha-ficticia-123"


@pytest.mark.parametrize("perfil", ["recepcionista", "profissional", "paciente"])
def test_cadastro_indisponivel_para_outros_perfis(perfil):
    cliente = cliente_teste()
    cliente.cadastrar_recepcionista = Mock()
    app = abrir_app(conta_teste(perfil), cliente)
    app.session_state[cadastro.ABERTO] = True
    app.run()
    assert not app.exception
    assert not any(botao.key == "menu-cadastrar-recepcionista" for botao in app.button)
    assert not any(campo.key == cadastro.SENHA for campo in app.text_input)
    assert cadastro.ABERTO not in app.session_state
    cliente.cadastrar_recepcionista.assert_not_called()


def abrir_formulario(erro=None):
    cliente = cliente_teste()
    cliente.cadastrar_recepcionista = Mock(return_value=23, side_effect=erro)
    app = abrir_app(conta_teste("administrador"), cliente)
    app.button(key="menu-cadastrar-recepcionista").click().run()
    assert not app.exception
    app.text_input(key=cadastro.NOME).set_value("Pessoa Fictícia")
    app.text_input(key=cadastro.EMAIL).set_value("equipe@example.invalid")
    app.text_input(key=cadastro.SENHA).set_value(SENHA)
    return app, cliente


def enviar(app, confirmacao=SENHA):
    app.text_input(key=cadastro.CONFIRMACAO).set_value(confirmacao)
    next(botao for botao in app.button if
         botao.label == "Cadastrar recepcionista" and botao.key != "menu-cadastrar-recepcionista").click()
    app.run()
    assert not app.exception


def test_cadastro_confirma_envio_unico_limpa_formulario_e_cache():
    app, cliente = abrir_formulario()
    credencial = app.session_state[sessao.CHAVE]
    hash_token = sha256(credencial.token.encode("utf-8")).hexdigest()
    app.session_state["xano_get_cache"] = {(hash_token, "contas-acesso"): object()}
    enviar(app)
    cliente.cadastrar_recepcionista.assert_called_once_with(
        credencial.token, "Pessoa Fictícia", "equipe@example.invalid", SENHA,
    )
    assert any("Recepcionista cadastrado" in mensagem.value for mensagem in app.success)
    assert app.session_state[sessao.CHAVE] == credencial
    assert (hash_token, "contas-acesso") not in app.session_state["xano_get_cache"]
    assert all(chave not in app.session_state for chave in (
        cadastro.ABERTO, cadastro.NOME, cadastro.EMAIL, cadastro.SENHA, cadastro.CONFIRMACAO,
    ))
    app.run()
    assert cliente.cadastrar_recepcionista.call_count == 1


@pytest.mark.parametrize("erro,mensagem", [
    (ErroAcesso("E-mail já cadastrado.", 409), "E-mail já cadastrado."),
    (ErroAcesso("Não foi possível confirmar o cadastro.", 503), "Não foi possível confirmar"),
    (ErroAcesso("Sua sessão expirou.", 401), "Sua sessão expirou."),
])
def test_cadastro_falho_preserva_nome_e_email_e_limpa_senhas(erro, mensagem):
    app, cliente = abrir_formulario(erro)
    enviar(app)
    assert any(mensagem in item.value for item in app.error)
    assert app.text_input(key=cadastro.NOME).value == "Pessoa Fictícia"
    assert app.text_input(key=cadastro.EMAIL).value == "equipe@example.invalid"
    assert app.text_input(key=cadastro.SENHA).value == ""
    assert app.text_input(key=cadastro.CONFIRMACAO).value == ""
    assert cliente.cadastrar_recepcionista.call_count == 1


def test_confirmacao_divergente_limpa_senhas_sem_enviar():
    app, cliente = abrir_formulario()
    enviar(app, "confirmacao-divergente")
    assert any("confirmação da senha não confere" in item.value for item in app.error)
    assert app.text_input(key=cadastro.SENHA).value == ""
    assert app.text_input(key=cadastro.CONFIRMACAO).value == ""
    cliente.cadastrar_recepcionista.assert_not_called()
