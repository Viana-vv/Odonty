from pathlib import Path

import pytest
import requests

from sorrisomais.api import ErroAcesso
from conftest import resposta


def test_catalogo_exclusivo_retorna_dados_minimos(cliente, http):
    http.return_value = resposta({"procedimentos": [{"id": 1, "nome": "Limpeza fictícia", "preco": 100}]})
    assert cliente.listar_procedimentos("token-ficticio") == [{"id": 1, "nome": "Limpeza fictícia"}]
    assert http.call_args.args == ("GET", "https://exemplo.invalid/api:teste/procedimentos")
    assert http.call_args.kwargs["headers"]["Authorization"] == "Bearer token-ficticio"


def test_catalogo_vazio(cliente, http):
    http.return_value = resposta({"procedimentos": []})
    assert cliente.listar_procedimentos("token-ficticio") == []


@pytest.mark.parametrize("payload", [{}, {"procedimentos": None}, {"procedimentos": [{"id": 1, "nome": ""}]}, {"procedimentos": [{"id": True, "nome": "Exemplo"}]}])
def test_catalogo_rejeita_contrato_invalido(cliente, http, payload):
    http.return_value = resposta(payload)
    with pytest.raises(ErroAcesso):
        cliente.listar_procedimentos("token-ficticio")


@pytest.mark.parametrize("status", [401, 403, 404, 429, 500, 503])
def test_catalogo_trata_falhas(cliente, http, status):
    http.return_value = resposta({"mensagem": "detalhe privado"}, status)
    with pytest.raises(ErroAcesso) as erro:
        cliente.listar_procedimentos("token-ficticio")
    assert erro.value.status == status
    assert "detalhe privado" not in str(erro.value)


def test_catalogo_sem_sessao_nao_envia(cliente, http):
    with pytest.raises(ErroAcesso):
        cliente.listar_procedimentos("")
    http.assert_not_called()


def test_catalogo_falha_de_conexao(cliente, http):
    http.side_effect = requests.Timeout()
    with pytest.raises(ErroAcesso):
        cliente.listar_procedimentos("token-ficticio")


def test_export_catalogo_autoriza_e_isola_consulta():
    codigo = (Path(__file__).resolve().parents[2] / "backend/xano/api/sorriso_acesso/procedimentos_GET.xs").read_text(encoding="utf-8-sig")
    assert 'auth = "conta_acesso"' in codigo
    assert 'perfis|intersect:["administrador", "recepcionista"]' in codigo
    assert 'sorriso_validar_sessao' in codigo
    assert '$db.procedimento.ativo == true' in codigo
    assert 'output = ["id", "nome"]' in codigo
    assert 'history = false' in codigo
    assert 'db.query paciente' not in codigo
    assert 'db.query profissional' not in codigo
