import pytest

from sorrisomais.api import ErroAcesso
from conftest import resposta


@pytest.mark.parametrize("status", [204, 401])
def test_post_logout_aceita_resposta_sem_corpo(cliente, http, status):
    http.return_value = resposta(status=status)
    assert cliente.sair("token-ficticio") is None
    assert http.call_args.args[:2] == ("POST", "https://exemplo.invalid/api:teste/auth/logout")
    http.return_value.json.assert_not_called()


def test_post_logout_nao_repete_requisicao_em_falha(cliente, http):
    http.side_effect = ErroAcesso("Falha segura.", 503)
    with pytest.raises(ErroAcesso):
        cliente.sair("token-ficticio")
    http.assert_called_once()
