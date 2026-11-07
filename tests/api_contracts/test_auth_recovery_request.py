from pathlib import Path

from sorrisomais.api import ErroAcesso
from conftest import resposta


def test_post_solicitar_recuperacao_envia_email_normalizado(cliente, http):
    http.return_value = resposta({"operacao_id": "op-ficticia"})
    assert cliente.solicitar_recuperacao(" Pessoa@Example.com ") == "op-ficticia"
    assert http.call_args.kwargs["json"] == {"email": "pessoa@example.com"}


def test_post_solicitar_recuperacao_rejeita_resposta_sem_operacao(cliente, http):
    http.return_value = resposta({})
    try:
        cliente.solicitar_recuperacao("pessoa@example.com")
    except ErroAcesso:
        pass
    else:
        raise AssertionError("resposta sem operação deveria ser rejeitada")


def test_xano_envia_otp_por_sendgrid():
    caminho = Path(__file__).resolve().parents[2] / "backend/xano/api/sorriso_acesso/auth/recuperacao-senha_POST.xs"
    codigo = caminho.read_text(encoding="utf-8-sig")
    assert "api.request" in codigo
    assert "$conta.email" in codigo
    assert '"type":"text/html"' in codigo
    assert "mascote-sorriso.png" in codigo
