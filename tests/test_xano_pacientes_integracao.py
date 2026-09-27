"""Integração opt-in do endpoint completo, com dados exclusivamente fictícios.

XANO_TESTAR_PACIENTE_INTEGRACAO=1 habilita criação de Paciente/Prontuário.
O grupo temporário é removido; cadastros de teste são inativados, não apagados.
"""

import os
import re
import secrets
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Barrier
from uuid import uuid4

import pytest
import requests

from test_xano_real import Ambiente, exigir_status
from test_xano_pacientes_real import cpf_ficticio


pytestmark = pytest.mark.skipif(
    os.getenv("XANO_TESTAR_PACIENTE_INTEGRACAO") != "1",
    reason="Integração de Paciente exige autorização explícita no ambiente.",
)


class CadastroReal(Ambiente):
    def __init__(self):
        super().__init__()
        self.tabelas = {t["name"]: t["id"] for t in self.listar("/table")}
        self.pacientes_criados = set()

    def enviar(self, dados, token=None, rota="/pacientes"):
        r = self.chamar("POST", rota, token or self.token, base=self.base_teste, json=dados)
        self.registrar(r)
        return r

    def registrar(self, resposta):
        if resposta.status_code == 201:
            self.pacientes_criados.add(resposta.json()["paciente"]["id"])

    def verificar(self, dados, token=None):
        r = self.chamar("POST", "/verificar", token or self.token, base=self.base_teste,
                       json={"cpf": dados["cpf"].replace(".", "").replace("-", ""),
                             "operacao_id": dados["operacao_id"]})
        exigir_status(r, 200)
        return r.json()


@pytest.fixture(scope="module")
def cadastro_real():
    a = CadastroReal()
    grupo = None
    try:
        conta = a.criar(["administrador"])
        a.token = a.entrar(conta)["token"]
        a.conta = conta
        slug = "integracao-paciente-" + secrets.token_hex(6)
        grupo = a.metadados("POST", "/apigroup", json={
            "name": slug, "canonical": slug, "swagger": False,
            "description": "Teste isolado de cadastro de Paciente e rollback",
        })
        a.grupo_teste = grupo["id"]
        a.base_teste = a.origem + "/api:" + slug
        codigo = Path("backend/xano/api/sorriso_acesso/pacientes_POST.xs").read_text(encoding="utf-8")
        codigo = re.sub(r'^\s*guid = .*$', '', codigo, flags=re.MULTILINE)
        codigo = codigo.replace('api_group = "Sorriso Acesso"', f'api_group = "{slug}"')
        falha = codigo.replace("query pacientes verb=", "query pacientes_falha verb=")
        marcador = "                db.add cadastro_paciente_operacao {"
        assert marcador in falha
        falha = falha.replace(marcador, '''                db.add prontuario_paciente {
                  data = {paciente_id: $novo_paciente.id, aberto_em: now, situacao: "ativo"}
                } as $duplicacao_induzida
''' + marcador)
        consulta = '''query verificar verb=POST {
  api_group = "GRUPO"
  auth = "conta_acesso"
  input {
    text cpf
    text operacao_id
  }
  stack {
    function.run sorriso_validar_sessao {
      input = {conta_id: $auth.id, sessao_id: $auth.extras.sessao_id}
    } as $sessao
    precondition ($auth.id == CONTA) {
      error_type = "accessdenied"
      error = "Acesso negado."
    }
    db.get paciente {
      field_name = "cpf"
      field_value = $input.cpf
      output = ["id"]
    } as $paciente
    var $paciente_id { value = $paciente|get:"id":0 }
    db.query paciente {
      where = $db.paciente.cpf == $input.cpf
      return = {type: "count"}
    } as $pacientes
    db.query prontuario_paciente {
      where = $db.prontuario_paciente.paciente_id == $paciente_id
      return = {type: "count"}
    } as $prontuarios
    db.query cadastro_paciente_operacao {
      where = $db.cadastro_paciente_operacao.conta_acesso_id == $auth.id && $db.cadastro_paciente_operacao.operacao_id == $input.operacao_id
      return = {type: "count"}
    } as $operacoes
  }
  response = {pacientes: $pacientes, prontuarios: $prontuarios, operacoes: $operacoes}
  history = false
}'''.replace("GRUPO", slug).replace("CONTA", str(conta["id"]))
        login_curto = Path("backend/xano/api/sorriso_acesso/auth/login_POST.xs").read_text(encoding="utf-8-sig")
        login_curto = re.sub(r'^\s*guid = .*$', '', login_curto, flags=re.MULTILINE)
        login_curto = login_curto.replace('api_group = "Sorriso Acesso"', f'api_group = "{slug}"')
        login_curto = login_curto.replace('$env|get:"AUTH_SESSION_TTL_SECONDS":3600|to_int', '2')
        for indice, fonte in enumerate((codigo, falha, consulta, login_curto), start=1):
            resposta = a.admin.post(a.meta + f"/apigroup/{grupo['id']}/api", data=fonte.encode("utf-8"),
                                   headers={"Content-Type": "text/x-xanoscript"}, timeout=30)
            if not resposta.ok:
                try:
                    detalhe = resposta.json()
                except ValueError:
                    detalhe = {"erro": "Resposta de compilação incompatível."}
                pytest.fail(f"Endpoint temporário {indice} não compilou (HTTP {resposta.status_code}): {detalhe}")
        yield a
    finally:
        for identificador in a.pacientes_criados:
            a.metadados("PUT", f"/table/{a.tabelas['paciente']}/content/{identificador}",
                        json={"situacao": "inativo"})
        if grupo:
            a.metadados("DELETE", f"/apigroup/{grupo['id']}")
        for identificador in a.criadas:
            a.alterar({"id": identificador}, situacao="inativo")
        a.admin.close()


@pytest.fixture
def cadastro_publicado():
    """Smoke opt-in do endpoint no grupo principal, após publicação explícita."""
    a = CadastroReal()
    a.base_teste = a.base
    try:
        conta = a.criar(["administrador"])
        a.token = a.entrar(conta)["token"]
        yield a
    finally:
        for identificador in a.pacientes_criados:
            a.metadados("PUT", f"/table/{a.tabelas['paciente']}/content/{identificador}",
                        json={"situacao": "inativo"})
        for identificador in a.criadas:
            a.alterar({"id": identificador}, situacao="inativo")
        a.admin.close()


@pytest.fixture
def payload():
    return {"nome": "Paciente Fictício Integração", "data_nascimento": "2000-02-29",
            "cpf": cpf_ficticio(), "email": "familia.ficticia@example.com",
            "telefone": "1133330000", "celular": "11999990000", "operacao_id": str(uuid4())}


def sucesso(resposta, dados):
    exigir_status(resposta, 201)
    corpo = resposta.json()
    assert set(corpo) == {"paciente", "operacao_id"}
    assert set(corpo["paciente"]) == {"id", "nome", "situacao"}
    assert corpo["paciente"]["id"] > 0
    assert corpo["paciente"]["nome"] == dados["nome"].strip()
    assert corpo["paciente"]["situacao"] == "ativo"
    assert corpo["operacao_id"] == dados["operacao_id"]
    assert resposta.headers.get("Cache-Control") == "no-store"
    return corpo


def test_hash_sem_chave_confirma_replay_e_divergencia(cadastro_real, payload):
    a = cadastro_real
    primeiro = sucesso(a.enviar(payload), payload)
    assert sucesso(a.enviar(payload), payload) == primeiro
    divergente = a.enviar(dict(payload, nome="Outro Paciente Fictício"))
    exigir_status(divergente, 409)
    assert divergente.json()["codigo"] == "OPERACAO_CONFLITANTE"
    assert a.verificar(payload) == {"pacientes": 1, "prontuarios": 1, "operacoes": 1}


def test_endpoint_publicado_cria_e_reconhece_replay(cadastro_publicado, payload):
    primeiro = sucesso(cadastro_publicado.enviar(payload), payload)
    assert sucesso(cadastro_publicado.enviar(payload), payload) == primeiro


def test_criacao_replay_e_payload_divergente(cadastro_real, payload):
    a = cadastro_real
    primeiro = sucesso(a.enviar(payload), payload)
    assert sucesso(a.enviar(payload), payload) == primeiro
    assert a.verificar(payload) == {"pacientes": 1, "prontuarios": 1, "operacoes": 1}
    divergente = dict(payload, nome="Outro Paciente Fictício")
    r = a.enviar(divergente)
    exigir_status(r, 409)
    assert r.json()["codigo"] == "OPERACAO_CONFLITANTE"
    assert a.verificar(payload) == {"pacientes": 1, "prontuarios": 1, "operacoes": 1}
    paciente = a.metadados("GET", f"/table/{a.tabelas['paciente']}/content/{primeiro['paciente']['id']}")
    assert all(paciente[c] == payload[c] for c in ("nome", "cpf", "telefone", "celular", "email", "data_nascimento"))
    assert paciente["situacao"] == "ativo" and paciente["criado_em"] and paciente["atualizado_em"]


def test_normalizacao_replay(cadastro_real, payload):
    normalizado = sucesso(cadastro_real.enviar(payload), payload)
    cpf = payload["cpf"]
    com_mascara = dict(payload, cpf=f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}",
                      nome=" " + payload["nome"] + " ", email=payload["email"].upper(),
                      telefone="(11) 3333-0000", celular="(11) 99999-0000")
    assert sucesso(cadastro_real.enviar(com_mascara), com_mascara) == normalizado


def test_cpf_duplicado_mesmo_inativo(cadastro_real, payload):
    a = cadastro_real
    primeiro = sucesso(a.enviar(payload), payload)
    a.metadados("PUT", f"/table/{a.tabelas['paciente']}/content/{primeiro['paciente']['id']}", json={"situacao":"inativo"})
    outro = dict(payload, operacao_id=str(uuid4()))
    r = a.enviar(outro)
    exigir_status(r, 409)
    assert r.json()["codigo"] == "CPF_DUPLICADO"
    assert a.verificar(outro) == {"pacientes": 1, "prontuarios": 1, "operacoes": 0}


def test_contatos_compartilhados(cadastro_real, payload):
    primeiro = sucesso(cadastro_real.enviar(payload), payload)
    outro = dict(payload, cpf=cpf_ficticio(), operacao_id=str(uuid4()))
    segundo = sucesso(cadastro_real.enviar(outro), outro)
    assert primeiro["paciente"]["id"] != segundo["paciente"]["id"]


@pytest.mark.parametrize("campo", ["nome", "data_nascimento", "cpf", "email", "telefone", "celular"])
@pytest.mark.parametrize("valor", [None, "", "   ", 123, "ausente"])
def test_campos_obrigatorios_sem_gravacao(cadastro_real, payload, campo, valor):
    invalido = dict(payload)
    if valor == "ausente":
        invalido.pop(campo)
    else:
        invalido[campo] = valor
    r = cadastro_real.enviar(invalido)
    exigir_status(r, 400)
    assert set(r.json()) == {"codigo", "mensagem"}
    assert r.json()["codigo"] == "DADOS_INVALIDOS"
    assert cadastro_real.verificar(payload) == {"pacientes": 0, "prontuarios": 0, "operacoes": 0}


@pytest.mark.parametrize("campo,valor", [("nome", "A"), ("nome", "A" * 121), ("email", "invalido"),
                                      ("telefone", "123"), ("celular", "+5511999990000"),
                                      ("cpf", "0" * 11), ("data_nascimento", "1900-02-29"),
                                      ("perfis", ["administrador"]), ("operacao_id", "invalido")])
def test_invalidos_extras_sem_gravacao(cadastro_real, payload, campo, valor):
    r = cadastro_real.enviar(dict(payload, **{campo: valor}))
    exigir_status(r, 400)
    assert r.json()["codigo"] == "DADOS_INVALIDOS"
    assert cadastro_real.verificar(payload) == {"pacientes": 0, "prontuarios": 0, "operacoes": 0}


@pytest.mark.parametrize("mudanca", [{"perfis":["profissional"]}, {"perfis":["paciente"]},
                                     {"perfis":[]}, {"situacao":"inativo"}, {"situacao":"bloqueado"}])
def test_autorizacao_atual(cadastro_real, payload, mudanca):
    a = cadastro_real
    conta = a.criar(["administrador"])
    token = a.entrar(conta)["token"]
    a.alterar(conta, **mudanca)
    exigir_status(a.enviar(payload, token), 403)
    assert a.verificar(payload) == {"pacientes": 0, "prontuarios": 0, "operacoes": 0}


def test_recepcionista_e_chave_por_conta(cadastro_real, payload):
    a = cadastro_real
    sucesso(a.enviar(payload), payload)
    conta = a.criar(["recepcionista"])
    token = a.entrar(conta)["token"]
    outro = dict(payload, cpf=cpf_ficticio())
    sucesso(a.enviar(outro, token), outro)
    exigir_status(a.chamar("POST", "/auth/logout", token), 204)
    exigir_status(a.enviar(outro, token), 401)


def test_sem_autenticacao(cadastro_real, payload):
    a = cadastro_real
    for token in (None, "token-invalido"):
        exigir_status(a.chamar("POST", "/pacientes", token, base=a.base_teste, json=payload), 401)
    assert a.verificar(payload) == {"pacientes": 0, "prontuarios": 0, "operacoes": 0}


@pytest.mark.parametrize("motivo", ["revogada", "expirada"])
def test_autorizacao_sessao_encerrada(cadastro_real, payload, motivo):
    a = cadastro_real
    conta = a.criar(["recepcionista"])
    if motivo == "expirada":
        token = a.entrar(conta, base=a.base_teste)["token"]
        time.sleep(3)
    else:
        token = a.entrar(conta)["token"]
        exigir_status(a.chamar("POST", "/auth/logout", token), 204)
    exigir_status(a.enviar(payload, token), 401)
    assert a.verificar(payload) == {"pacientes": 0, "prontuarios": 0, "operacoes": 0}


@pytest.mark.parametrize("corpo", ["[]", "null", "true"])
def test_corpo_invalido_sem_gravacao(cadastro_real, payload, corpo):
    a = cadastro_real
    r = a.chamar("POST", "/pacientes", a.token, base=a.base_teste, data=corpo)
    exigir_status(r, 400)
    assert r.json()["codigo"] == "DADOS_INVALIDOS"
    assert a.verificar(payload) == {"pacientes": 0, "prontuarios": 0, "operacoes": 0}


def test_schema_comprovante(cadastro_real):
    a = cadastro_real
    tabela = a.metadados("GET", f"/table/{a.tabelas['cadastro_paciente_operacao']}")
    campos = {c["name"]: c for c in tabela["schema"]}
    for campo in ("conta_acesso_id", "operacao_id", "paciente_id", "impressao_hmac"):
        assert campos[campo]["required"] and not campos[campo]["nullable"]
    assert any(i["type"] == "unique" and [f["name"] for f in i["fields"]] == ["conta_acesso_id", "operacao_id"] for i in tabela["index"])


def test_uuid_com_quebra_de_linha(cadastro_real, payload):
    r = cadastro_real.enviar(dict(payload, operacao_id=payload["operacao_id"] + "\n"))
    exigir_status(r, 400)
    assert cadastro_real.verificar(payload) == {"pacientes": 0, "prontuarios": 0, "operacoes": 0}


def test_rollback_por_falha_induzida(cadastro_real, payload):
    r = cadastro_real.enviar(payload, rota="/pacientes_falha")
    exigir_status(r, 503)
    assert r.json() == {"codigo": "SERVICO_INDISPONIVEL", "mensagem": "Não foi possível confirmar o cadastro."}
    assert cadastro_real.verificar(payload) == {"pacientes": 0, "prontuarios": 0, "operacoes": 0}
    sucesso(cadastro_real.enviar(payload), payload)


@pytest.mark.parametrize("mesma_operacao", [True, False])
def test_concorrencia(cadastro_real, payload, mesma_operacao):
    a = cadastro_real
    outro = dict(payload) if mesma_operacao else dict(payload, operacao_id=str(uuid4()))
    barreira = Barrier(2)
    def enviar(dados):
        barreira.wait(timeout=10)
        return requests.post(a.base_teste + "/pacientes", json=dados,
                             headers={"Authorization": "Bearer " + a.token}, timeout=40)
    time.sleep(8)
    with ThreadPoolExecutor(max_workers=2) as executor:
        respostas = list(executor.map(enviar, [payload, outro]))
    for r in respostas:
        a.registrar(r)
    assert sorted(r.status_code for r in respostas) == ([201, 201] if mesma_operacao else [201, 409])
    if mesma_operacao:
        assert respostas[0].json() == respostas[1].json()
    else:
        assert next(r for r in respostas if r.status_code == 409).json()["codigo"] == "CPF_DUPLICADO"
    confirmada = a.verificar(payload)
    assert confirmada["pacientes"] == 1
    assert confirmada["prontuarios"] == 1
    if mesma_operacao:
        assert confirmada["operacoes"] == 1
    else:
        confirmada_outra = a.verificar(outro)
        assert confirmada["operacoes"] + confirmada_outra["operacoes"] == 1


def test_historico_desativado(cadastro_real):
    a = cadastro_real
    dados = a.metadados("GET", "/request_history", params={"apigroup_id": a.grupo_teste, "per_page":100})
    assert not dados.get("items", [])
