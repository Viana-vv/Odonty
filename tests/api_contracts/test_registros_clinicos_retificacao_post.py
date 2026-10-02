import pytest

from conftest import resposta
from sorrisomais.contratos_clinicos import DadosContratoInvalidos
from sorrisomais.api import ErroAcesso


def test_post_retificacoes_acrescenta_nova_versao_com_justificativa(cliente, http):
    http.return_value = resposta({"retificacao": {
        "id": 7, "registro_clinico_id": 2, "profissional_id": 8,
    }}, 201)
    resultado = cliente.retificar_registro_clinico(
        "token-ficticio", 2, "Conteúdo corrigido fictício", "Correção de digitação",
    )
    assert resultado["id"] == 7
    assert http.call_args.args[:2] == (
        "POST", "https://exemplo.invalid/api:teste/registros-clinicos/2/retificacoes",
    )
    assert http.call_args.kwargs["json"] == {
        "conteudo": "Conteúdo corrigido fictício", "justificativa": "Correção de digitação",
    }


def test_post_retificacoes_exige_justificativa(cliente, http):
    with pytest.raises(DadosContratoInvalidos):
        cliente.retificar_registro_clinico("token-ficticio", 2, "Novo conteúdo", " ")
    http.assert_not_called()


def test_post_retificacoes_nao_expoe_resposta_interna_em_conflito(cliente, http):
    http.return_value = resposta({"erro": "detalhe clínico interno"}, 409)
    with pytest.raises(ErroAcesso) as erro:
        cliente.retificar_registro_clinico(
            "token-ficticio", 2, "Conteúdo fictício", "Justificativa fictícia",
        )
    assert erro.value.status == 409
    assert "detalhe clínico interno" not in str(erro.value)
