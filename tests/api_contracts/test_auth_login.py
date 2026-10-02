import pytest

from sorrisomais.api import ErroAcesso
from conftest import FUTURO, resposta


def test_post_login_envia_payload_e_valida_token(cliente, http):
    http.return_value = resposta({
        "token": "token-ficticio", "tipo_token": "Bearer", "expira_em": FUTURO.isoformat(),
    })
    credencial = cliente.entrar("PESSOA@example.com", "senha-ficticia")
    assert http.call_args.args[:2] == ("POST", "https://exemplo.invalid/api:teste/auth/login")
    assert http.call_args.kwargs["json"] == {"email": "pessoa@example.com", "senha": "senha-ficticia"}
    assert http.call_args.kwargs["allow_redirects"] is False
    assert "token-ficticio" not in repr(credencial)


@pytest.mark.parametrize("payload", [None, [], {}, {"token": "t", "tipo_token": "Errado"}])
def test_post_login_rejeita_respostas_invalidas(cliente, http, payload):
    http.return_value = resposta(payload)
    with pytest.raises(ErroAcesso):
        cliente.entrar("pessoa@example.com", "senha-ficticia")


def test_post_login_nao_exibe_corpo_de_erro(cliente, http):
    http.return_value = resposta({"mensagem": "SEGREDO"}, 401)
    with pytest.raises(ErroAcesso) as erro:
        cliente.entrar("pessoa@example.com", "senha-ficticia")
    assert "SEGREDO" not in str(erro.value)
