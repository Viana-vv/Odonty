import pytest
import requests

from sorrisomais.api import ErroAcesso
from conftest import FUTURO, resposta


def test_get_identidade_envia_bearer_e_valida_conta(cliente, http):
    http.return_value = resposta({
        "conta": {"id": 4, "nome": "Dentista Fictício", "perfis": ["profissional"], "situacao": "ativo"},
        "expira_em": FUTURO.isoformat(),
    })
    conta = cliente.identificar("token-ficticio")
    assert conta.id == 4
    assert conta.perfis == ("profissional",)
    assert http.call_args.args[:2] == ("GET", "https://exemplo.invalid/api:teste/auth/me")
    assert http.call_args.kwargs["headers"]["Authorization"] == "Bearer token-ficticio"


@pytest.mark.parametrize("perfis", [["paciente"], ["inventado"], ["profissional", "profissional"], [1]])
def test_get_identidade_rejeita_perfis_invalidos(cliente, http, perfis):
    http.return_value = resposta({
        "conta": {"id": 4, "nome": "Conta Fictícia", "perfis": perfis, "situacao": "ativo"},
        "expira_em": FUTURO.isoformat(),
    })
    with pytest.raises(ErroAcesso):
        cliente.identificar("token-ficticio")


def test_get_identidade_omite_detalhe_de_falha_de_rede(cliente, http):
    http.side_effect = requests.Timeout("authorization=secreto")
    with pytest.raises(ErroAcesso) as erro:
        cliente.identificar("token-ficticio")
    assert "secreto" not in str(erro.value)
