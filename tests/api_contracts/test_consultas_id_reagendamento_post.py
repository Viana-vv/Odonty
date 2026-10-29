"""Contrato POST /consultas/{id}/reagendamento, sempre sem rede."""
from copy import deepcopy
from pathlib import Path

import pytest
import requests

from sorrisomais.api import ErroAcesso
from sorrisomais.contratos_clinicos import DadosContratoInvalidos
from sorrisomais.reagendamento_consulta import reagendar_consulta
from conftest import resposta


RESULTADO = {
    "consulta_original": {"id": 10, "paciente_id": 4, "profissional_id": 8,
                          "disponibilidade_id": 3, "situacao": "Cancelada"},
    "consulta": {"id": 11, "paciente_id": 4, "profissional_id": 9,
                 "disponibilidade_id": 5, "situacao": "Agendada"},
    "reagendamento_id": 1,
}


def test_reagendamento_envia_uma_unica_operacao_sem_paciente_ou_profissional(cliente, http):
    http.return_value = resposta(deepcopy(RESULTADO), 201)
    resultado = reagendar_consulta(cliente, "token-ficticio", 10, 5, "  Solicitação fictícia  ")
    assert resultado == RESULTADO
    assert http.call_count == 1
    assert http.call_args.args == (
        "POST", "https://exemplo.invalid/api:teste/consultas/10/reagendamento",
    )
    assert http.call_args.kwargs["json"] == {
        "disponibilidade_id": 5, "justificativa": "Solicitação fictícia",
    }
    assert http.call_args.kwargs["headers"]["Authorization"] == "Bearer token-ficticio"


@pytest.mark.parametrize("consulta,horario,justificativa", [
    (0, 5, "Motivo"), (True, 5, "Motivo"), ("10", 5, "Motivo"),
    (10, 0, "Motivo"), (10, True, "Motivo"), (10, 5, "   "),
    (10, 5, None), (10, 5, "x" * 1001),
])
def test_campos_invalidos_nao_enviam_requisicao(cliente, http, consulta, horario, justificativa):
    with pytest.raises(DadosContratoInvalidos):
        reagendar_consulta(cliente, "token-ficticio", consulta, horario, justificativa)
    http.assert_not_called()


def test_sessao_ausente_nao_envia_requisicao(cliente, http):
    with pytest.raises(ErroAcesso) as erro:
        reagendar_consulta(cliente, None, 10, 5, "Motivo")
    assert erro.value.status == 401
    http.assert_not_called()


@pytest.mark.parametrize("status", [400, 401, 403, 404, 409, 503])
def test_erros_do_backend_sem_repeticao_ou_detalhes_sensiveis(cliente, http, status):
    http.return_value = resposta({"mensagem": "Detalhe interno secreto"}, status)
    with pytest.raises(ErroAcesso) as erro:
        reagendar_consulta(cliente, "token-ficticio", 10, 5, "Motivo")
    assert erro.value.status == status
    assert "secreto" not in str(erro.value)
    assert http.call_count == 1


def test_falha_de_conexao_nao_repete_mutacao(cliente, http):
    http.side_effect = requests.ConnectionError("Detalhe interno secreto")
    with pytest.raises(ErroAcesso) as erro:
        reagendar_consulta(cliente, "token-ficticio", 10, 5, "Motivo")
    assert "secreto" not in str(erro.value)
    assert http.call_count == 1


@pytest.mark.parametrize("campo,valor", [
    ("reagendamento_id", None), ("reagendamento_id", True),
    ("consulta_original", None), ("consulta", {}),
])
def test_resposta_incompleta_nao_confirma_sucesso(cliente, http, campo, valor):
    dados = deepcopy(RESULTADO)
    dados[campo] = valor
    http.return_value = resposta(dados, 201)
    with pytest.raises(ErroAcesso):
        reagendar_consulta(cliente, "token-ficticio", 10, 5, "Motivo")


@pytest.mark.parametrize("recurso,campo,valor", [
    ("consulta_original", "id", 30), ("consulta_original", "situacao", "Confirmada"),
    ("consulta", "situacao", "Cancelada"), ("consulta", "id", 10),
    ("consulta", "paciente_id", 33), ("consulta", "disponibilidade_id", 9),
    ("consulta_original", "disponibilidade_id", 5),
])
def test_resposta_inconsistente_nao_confirma_sucesso(cliente, http, recurso, campo, valor):
    dados = deepcopy(RESULTADO)
    dados[recurso][campo] = valor
    http.return_value = resposta(dados, 201)
    with pytest.raises(ErroAcesso):
        reagendar_consulta(cliente, "token-ficticio", 10, 5, "Motivo")


def test_export_persiste_vinculo_e_historico_dentro_da_transacao():
    raiz = Path(__file__).resolve().parents[2]
    fonte = (raiz / "backend/xano/api/sorriso_acesso/consultas_id_reagendamento_POST.xs").read_text(encoding="utf-8")
    transacao = fonte.split("db.transaction", 1)[1].split("catch {", 1)[0]
    for operacao in ("db.add consulta {", "db.add consulta_reagendamento {",
                     "db.add consulta_disponibilidade {", "db.edit consulta {",
                     "db.add consulta_situacao_historico {", "db.edit disponibilidade_agenda {"):
        assert operacao in transacao
    assert "consulta_original_id: $consulta.id" in transacao
    assert "consulta_nova_id: $nova_consulta.id" in transacao
    assert "$db.consulta.id != $consulta.id" in transacao
    assert "db.delete" not in fonte
    assert "db.add consulta_procedimento" not in fonte
    assert "db.edit registro_clinico" not in fonte
    assert 'auth = "conta_acesso"' in fonte
    assert "function.run sorriso_validar_sessao" in fonte
    assert 'intersect:["administrador", "recepcionista"]' in fonte
    assert "history = false" in fonte


def test_tabela_de_reagendamento_e_aditiva_com_origem_e_destino_unicos():
    raiz = Path(__file__).resolve().parents[2]
    fonte = (raiz / "backend/xano/table/consulta_reagendamento.xs").read_text(encoding="utf-8")
    assert fonte.count('table = "consulta"') == 2
    assert fonte.count('type: "btree|unique"') == 2
    for campo in ("consulta_original_id", "consulta_nova_id", "conta_acesso_id", "justificativa", "criado_em"):
        assert campo in fonte
