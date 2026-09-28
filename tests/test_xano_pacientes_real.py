"""Validação real do cadastro em grupo temporário, sem gravar Pacientes.

Exige XANO_TESTAR_PACIENTE=1 e as configurações administrativas de teste.
Compila o trecho de validação do endpoint versionado e o executa no Xano.
Não comprova a transação nem a idempotência do endpoint completo.
"""

import os
import secrets
from datetime import timedelta
from pathlib import Path
from uuid import uuid4

import pytest

from sorrisomais.pacientes import hoje
from test_xano_real import Ambiente, exigir_status


pytestmark = pytest.mark.skipif(
    os.getenv("XANO_TESTAR_PACIENTE") != "1",
    reason="Validação real de Paciente exige configuração explícita.",
)


def cpf_ficticio():
    """Número sintético; não é obtido de cadastro ou pessoa real."""
    digitos = [secrets.randbelow(10) for _ in range(9)]
    if len(set(digitos)) == 1:
        digitos[0] = (digitos[0] + 1) % 10
    for tamanho in (9, 10):
        resto = sum(d * p for d, p in zip(digitos, range(tamanho + 1, 1, -1))) % 11
        digitos.append(0 if resto < 2 else 11 - resto)
    return "".join(map(str, digitos))


@pytest.fixture(scope="module")
def validacao_real():
    ambiente = Ambiente()
    grupo = None
    try:
        conta = ambiente.criar(["administrador"])
        token = ambiente.entrar(conta)["token"]
        slug = "validacao-paciente-" + secrets.token_hex(6)
        grupo = ambiente.metadados("POST", "/apigroup", json={
            "name": slug, "canonical": slug, "swagger": False,
            "description": "Verificacao temporaria das validacoes de Paciente",
        })
        codigo = Path("backend/xano/api/sorriso_acesso/pacientes_POST.xs").read_text(encoding="utf-8")
        # Executa a mesma validação do endpoint, interrompendo antes de qualquer gravação.
        codigo, separador, _ = codigo.partition("    // O hash HMAC")
        assert separador, "Delimitador do trecho de validação não encontrado."
        codigo = codigo.replace('api_group = "Sorriso Acesso"', f'api_group = "{slug}"')
        codigo += '\n    util.set_header { value = "HTTP/1.1 204 No Content" }\n  }\n  response = null\n  history = false\n}\n'
        ambiente.metadados("POST", f"/apigroup/{grupo['id']}/api",
                          data=codigo.encode("utf-8"),
                          headers={"Content-Type": "text/x-xanoscript"})
        yield ambiente, token, ambiente.origem + "/api:" + slug
    finally:
        if grupo:
            ambiente.metadados("DELETE", f"/apigroup/{grupo['id']}")
        for identificador in ambiente.criadas:
            ambiente.alterar({"id": identificador}, situacao="inativo")
        ambiente.admin.close()


@pytest.fixture
def dados_validos():
    return {"nome": "Paciente Fictício de Verificação", "data_nascimento": "2000-02-29",
            "cpf": cpf_ficticio(), "email": "paciente.ficticio@example.com",
            "telefone": "(11) 3333-0000", "celular": "(11) 99999-0000",
            "operacao_id": str(uuid4())}


def verificar(validacao_real, dados, status):
    ambiente, token, base = validacao_real
    resposta = ambiente.chamar("POST", "/pacientes", token, base=base, json=dados)
    exigir_status(resposta, status)
    assert resposta.headers.get("Cache-Control") == "no-store"
    if status == 400:
        assert resposta.json() == {"codigo": "DADOS_INVALIDOS", "mensagem": "Confira os dados informados."}
    return resposta


@pytest.mark.parametrize("nascimento", ["0001-01-01", "1900-02-28", "2000-02-29", "2024-02-29", "hoje"])
def test_datas_validas_no_backend(validacao_real, dados_validos, nascimento):
    dados_validos["data_nascimento"] = hoje().isoformat() if nascimento == "hoje" else nascimento
    verificar(validacao_real, dados_validos, 204)


@pytest.mark.parametrize("nascimento", [
    "0000-01-01", "1900-02-29", "2023-02-29", "2000-02-30", "2000-04-31",
    "2000-00-01", "2000-13-01", "2000-01-00", "2000-01-32", "amanha",
    "2000-1-01", "2000-01-01\n", " 2000-01-01", "2000-01-01T00:00:00",
])
def test_datas_invalidas_no_backend(validacao_real, dados_validos, nascimento):
    dados_validos["data_nascimento"] = (hoje() + timedelta(days=1)).isoformat() if nascimento == "amanha" else nascimento
    verificar(validacao_real, dados_validos, 400)


@pytest.mark.parametrize("alteracao", ["primeiro", "segundo", "repetido", "mascara", "unicode"])
def test_cpf_invalido_no_backend(validacao_real, dados_validos, alteracao):
    cpf = dados_validos["cpf"]
    if alteracao in ("primeiro", "segundo"):
        indice = 9 if alteracao == "primeiro" else 10
        cpf = cpf[:indice] + str((int(cpf[indice]) + 1) % 10) + cpf[indice + 1:]
    elif alteracao == "repetido":
        cpf = "0" * 11
    elif alteracao == "mascara":
        cpf = cpf[:2] + "." + cpf[2:]
    else:
        cpf = "".join(chr(ord("０") + int(d)) for d in cpf)
    dados_validos["cpf"] = cpf
    verificar(validacao_real, dados_validos, 400)


def test_cpf_com_mascara_no_backend(validacao_real, dados_validos):
    cpf = dados_validos["cpf"]
    dados_validos["cpf"] = f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
    verificar(validacao_real, dados_validos, 204)


def test_schema_cpf_unico_e_situacao(validacao_real):
    ambiente, _, _ = validacao_real
    tabela = ambiente.metadados("GET", "/table/883766")
    campos = {c["name"]: c for c in tabela["schema"]}
    assert campos["situacao"]["values"] == ["ativo", "inativo"]
    assert campos["atualizado_em"]["type"] == "timestamp"
    assert any(i["type"] == "unique" and [f["name"] for f in i["fields"]] == ["cpf"] for i in tabela["index"])
