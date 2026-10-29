from datetime import datetime, timedelta, timezone
from unittest.mock import Mock

import pytest
from streamlit.testing.v1 import AppTest

from sorrisomais import autoatendimento_paciente, sessao_paciente
from sorrisomais.api import ContaAcesso, Credencial, ErroAcesso


class ClienteFake:
    def __init__(self):
        self.credencial = None
        self.consultas = [{
            "id": 1, "inicio_em": (datetime.now(timezone.utc) + timedelta(days=2)).isoformat(),
            "fim_em": "", "profissional_nome": "Dra. Fictícia", "situacao": "Confirmada",
            "procedimentos": ["NÃO EXIBIR PROCEDIMENTO"],
        }]
        self.registros = [{
            "id": 2, "paciente_id": 4, "profissional_id": 8, "prontuario_id": 3,
            "conteudo": "Orientação fictícia liberada", "liberado_paciente": True,
            "registrado_em": datetime.now(timezone.utc).isoformat(),
        }]
        self.exames = [{
            "id": 3, "paciente_id": 4, "consulta_id": 1, "tipo": "Radiografia fictícia",
            "situacao": "Resultado disponível", "solicitado_em": datetime.now(timezone.utc).isoformat(),
            "realizado_em": None, "resultado": "Resultado fictício liberado",
            "observacoes": "OBSERVAÇÃO PRIVADA", "arquivo_url": "URL PRIVADA",
        }]

    def entrar(self, email, senha):
        self.credencial = Credencial("token-ficticio", datetime.now(timezone.utc) + timedelta(hours=1))
        return self.credencial

    def identificar(self, token):
        return ContaAcesso(4, "Paciente Fictício", ("paciente",), self.credencial.expira_em)

    def listar_consultas(self, token):
        assert token == "token-ficticio"
        return self.consultas

    def listar_registros_clinicos(self, token):
        assert token == "token-ficticio"
        return self.registros

    def _request(self, method, route, **kwargs):
        assert method == "GET" and route == "/exames"
        assert kwargs["token"] == "token-ficticio"
        assert kwargs["params"] is None
        return {"exames": self.exames}


def test_entrada_paciente_guarda_sessao_temporaria_sem_senha():
    estado = {}
    cliente = Mock()
    credencial = Credencial("token-ficticio", datetime.now(timezone.utc) + timedelta(hours=1))
    conta = ContaAcesso(4, "Paciente Fictício", ("paciente",), credencial.expira_em)
    cliente.entrar.return_value = credencial
    cliente.identificar.return_value = conta

    sessao_paciente.entrar(estado, cliente, "paciente@exemplo.invalid", "senha-ficticia")

    assert estado[sessao_paciente.CHAVE_CREDENCIAL] == credencial
    assert estado[sessao_paciente.CHAVE_CONTA] == conta
    assert "senha-ficticia" not in repr(estado)


def test_entrada_de_perfil_interno_nao_concede_portal_paciente():
    estado = {}
    cliente = Mock()
    credencial = Credencial("token-ficticio", datetime.now(timezone.utc) + timedelta(hours=1))
    cliente.entrar.return_value = credencial
    cliente.identificar.return_value = ContaAcesso(5, "Profissional Fictício", ("profissional",), credencial.expira_em)

    with pytest.raises(ErroAcesso, match="exclusiva para Pacientes"):
        sessao_paciente.entrar(estado, cliente, "profissional@exemplo.invalid", "senha-ficticia")

    cliente.sair.assert_called_once_with("token-ficticio")
    assert sessao_paciente.CHAVE_CREDENCIAL not in estado


def test_expiracao_limpa_sessao_paciente():
    estado = {sessao_paciente.CHAVE_CREDENCIAL: Credencial("token-ficticio", datetime.now(timezone.utc) - timedelta(seconds=1))}
    cliente = Mock()

    with pytest.raises(ErroAcesso, match="expirou"):
        sessao_paciente.identificar(estado, cliente)

    assert estado == {}
    cliente.identificar.assert_not_called()


def test_logout_limpa_credenciais_e_tenta_revogar_sessao():
    estado = {sessao_paciente.CHAVE_CREDENCIAL: Credencial("token-ficticio", datetime.now(timezone.utc) + timedelta(hours=1))}
    cliente = Mock()

    assert "segurança" in sessao_paciente.sair(estado, cliente)
    cliente.sair.assert_called_once_with("token-ficticio")
    assert estado == {}


def _renderizar_portal(cliente):
    from sorrisomais.autoatendimento_paciente import renderizar
    renderizar(cliente)


def test_portal_apresenta_conteudo_proprio_sem_campos_privados():
    cliente = ClienteFake()
    app = AppTest.from_function(_renderizar_portal, args=(cliente,)).run()
    expiry = datetime.now(timezone.utc) + timedelta(hours=1)
    cliente.credencial = Credencial("token-ficticio", expiry)
    app.session_state[sessao_paciente.CHAVE_CREDENCIAL] = cliente.credencial
    app.session_state[sessao_paciente.CHAVE_CONTA] = ContaAcesso(4, "Paciente Fictício", ("paciente",), expiry)
    app.run()

    assert not app.exception
    texto = " ".join([x.value for grupo in (app.markdown, app.caption, app.text) for x in grupo])
    assert "Dra. Fictícia" in texto
    assert "Orientação fictícia liberada" in texto
    assert "Resultado fictício liberado" in texto
    assert "NÃO EXIBIR PROCEDIMENTO" not in texto
    assert "OBSERVAÇÃO PRIVADA" not in texto
    assert "URL PRIVADA" not in texto



def test_login_paciente_limpa_senha_e_abre_portal():
    cliente = ClienteFake()
    app = AppTest.from_function(_renderizar_portal, args=(cliente,)).run()
    app.text_input(key="paciente_email").set_value("paciente@exemplo.invalid")
    app.text_input(key="paciente_senha").set_value("senha-ficticia")
    app.button[0].click().run()

    assert not app.exception
    assert any(item.value == "Olá, Paciente Fictício" for item in app.title)
    assert "senha-ficticia" not in repr(dict(app.session_state))
    assert app.session_state[sessao_paciente.CHAVE_CREDENCIAL].token == "token-ficticio"


def test_login_paciente_exibe_erro_sem_manter_senha():
    cliente = ClienteFake()
    cliente.entrar = Mock(side_effect=ErroAcesso("E-mail ou senha incorretos, ou conta indisponível.", 401))
    app = AppTest.from_function(_renderizar_portal, args=(cliente,)).run()
    app.text_input(key="paciente_email").set_value("paciente@exemplo.invalid")
    app.text_input(key="paciente_senha").set_value("senha-ficticia")
    app.button[0].click().run()

    assert not app.exception
    assert any("E-mail ou senha incorretos" in item.value for item in app.error)
    assert "senha-ficticia" not in repr(dict(app.session_state))
    assert app.session_state.get("paciente_senha", "") == ""
    assert sessao_paciente.CHAVE_CREDENCIAL not in app.session_state


@pytest.mark.parametrize("etapa,erro", [
    ("entrar", ErroAcesso("Não foi possível conectar ao serviço. Tente novamente em instantes.")),
    ("identificar", ErroAcesso("Sua conta não tem permissão para acessar esta área.", 403)),
])
def test_login_paciente_limpa_senha_em_falha_de_rede_ou_identidade(etapa, erro):
    cliente = ClienteFake()
    setattr(cliente, etapa, Mock(side_effect=erro))
    cliente.sair = Mock()
    app = AppTest.from_function(_renderizar_portal, args=(cliente,)).run()
    app.text_input(key="paciente_email").set_value("paciente@exemplo.invalid")
    app.text_input(key="paciente_senha").set_value("senha-ficticia")
    app.button[0].click().run()

    assert not app.exception
    assert any(str(erro) in item.value for item in app.error)
    assert "senha-ficticia" not in repr(dict(app.session_state))
    assert app.session_state.get("paciente_senha", "") == ""
    assert sessao_paciente.CHAVE_CREDENCIAL not in app.session_state


def test_tela_login_paciente_nao_exibe_instrucao_de_endereco_da_equipe():
    app = AppTest.from_function(_renderizar_portal, args=(ClienteFake(),)).run()

    assert not app.exception
    texto = " ".join(item.value for grupo in (app.caption, app.markdown, app.text) for item in grupo)
    assert "Acesso pessoal do Paciente" not in texto
    assert "A equipe utiliza outro endereço" not in texto
    assert any(item.value == "Entre na sua conta" for item in app.title)
