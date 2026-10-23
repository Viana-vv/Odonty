from pathlib import Path

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


def test_post_login_xano_autentica_conta_paciente_ativa():
    caminho = (Path(__file__).resolve().parents[2] / "backend" / "xano" / "api"
               / "sorriso_acesso" / "auth" / "login_POST.xs")
    codigo = caminho.read_text(encoding="utf-8-sig")

    assert '"paciente"' in codigo
    assert "$conta.situacao != \"ativo\"" in codigo
    assert "security.check_password" in codigo
    assert "security.create_auth_token" in codigo


def test_post_login_xano_usa_limite_de_sessao_de_oito_horas():
    caminho = (Path(__file__).resolve().parents[2] / "backend" / "xano" / "api"
               / "sorriso_acesso" / "auth" / "login_POST.xs")
    codigo = caminho.read_text(encoding="utf-8-sig")

    assert '$env|get:"AUTH_SESSION_TTL_SECONDS":28800|to_int' in codigo
    assert "precondition ($duracao > 0 && $duracao <= 28800)" in codigo
    assert "expira_em: $prazo" in codigo
    assert "expiration = $duracao" in codigo
