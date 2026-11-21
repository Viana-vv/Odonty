from pathlib import Path

import pytest
import requests

from sorrisomais.api import ErroAcesso
from conftest import resposta


def test_get_pacientes_independe_das_opcoes_da_agenda(cliente, http):
    http.return_value = resposta({
        "pacientes": [{"id": 11, "nome": "Paciente Fictícia Aurora", "telefone": "privado"}],
    })
    assert cliente.listar_pacientes("token-ficticio") == [
        {"id": 11, "nome": "Paciente Fictícia Aurora"},
    ]
    http.assert_called_once()
    assert http.call_args.args == ("GET", "https://exemplo.invalid/api:teste/pacientes")
    assert http.call_args.kwargs["headers"]["Authorization"] == "Bearer token-ficticio"


def test_get_pacientes_aceita_lista_vazia(cliente, http):
    http.return_value = resposta({"pacientes": []})
    assert cliente.listar_pacientes("token-ficticio") == []


@pytest.mark.parametrize("payload", [
    {}, {"pacientes": None}, {"pacientes": {}},
    {"pacientes": [{"id": 1, "nome": ""}]},
    {"pacientes": [{"id": True, "nome": "Fictício"}]},
    {"pacientes": [{"id": 1}]},
    {"pacientes": [{"id": 1, "nome": "Fictício"}] * 2},
])
def test_get_pacientes_recusa_resposta_invalida(cliente, http, payload):
    http.return_value = resposta(payload)
    with pytest.raises(ErroAcesso):
        cliente.listar_pacientes("token-ficticio")


@pytest.mark.parametrize("status", [401, 403, 404, 429, 500, 503])
def test_get_pacientes_trata_erros_sem_expor_corpo(cliente, http, status):
    http.return_value = resposta({"mensagem": "detalhe privado"}, status)
    with pytest.raises(ErroAcesso) as erro:
        cliente.listar_pacientes("token-ficticio")
    assert erro.value.status == status
    assert "detalhe privado" not in str(erro.value)


def test_get_pacientes_exige_token_antes_da_rede(cliente, http):
    with pytest.raises(ErroAcesso) as erro:
        cliente.listar_pacientes("")
    assert erro.value.status == 401
    http.assert_not_called()


def test_get_pacientes_trata_falha_de_conexao(cliente, http):
    http.side_effect = requests.ConnectionError("detalhe privado")
    with pytest.raises(ErroAcesso) as erro:
        cliente.listar_pacientes("token-ficticio")
    assert "Não foi possível conectar" in str(erro.value)
    assert "detalhe privado" not in str(erro.value)


def test_export_xano_pacientes_autoriza_e_consulta_somente_pacientes():
    codigo = (Path(__file__).resolve().parents[2] / "backend/xano/api/sorriso_acesso/pacientes_GET.xs").read_text(encoding="utf-8-sig")
    assert 'auth = "conta_acesso"' in codigo
    assert "function.run sorriso_validar_sessao" in codigo
    assert 'perfis|intersect:["administrador", "recepcionista"]' in codigo
    assert '$solicitante.situacao != "ativo"' in codigo
    assert "403 Forbidden" in codigo
    assert '$db.paciente.situacao == "ativo"' in codigo
    assert 'sort = {paciente.nome: "asc", paciente.id: "asc"}' in codigo
    assert 'output = ["id", "nome"]' in codigo
    assert 'response = {pacientes: $pacientes}' in codigo
    assert "Cache-Control: no-store" in codigo
    assert "history = false" in codigo
    assert "db.query profissional" not in codigo
    assert "db.query procedimento" not in codigo
