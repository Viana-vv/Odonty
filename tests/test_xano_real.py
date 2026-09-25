"""Testes reais opt-in. Criam contas ficticias e as inativam ao terminar.

Executar somente com XANO_TESTAR_REAL=1, XANO_API_BASE_URL,
XANO_METADATA_TOKEN e XANO_WORKSPACE_ID configurados no ambiente.
Nenhum segredo ou corpo de autenticacao e registrado.
"""
import os
import re
import secrets
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

import pytest
import requests

pytestmark = pytest.mark.skipif(
    os.getenv("XANO_TESTAR_REAL") != "1",
    reason="Integracao real exige configuracao explicita.",
)


class Ambiente:
    def __init__(self):
        self.ultima_chamada = 0.0
        self.base = os.environ["XANO_API_BASE_URL"].rstrip("/")
        partes = urlsplit(self.base)
        assert partes.scheme == "https" and not partes.username
        self.origem = f"{partes.scheme}://{partes.netloc}"
        self.meta = self.origem + "/api:meta/workspace/" + os.environ["XANO_WORKSPACE_ID"]
        self.admin = requests.Session()
        self.admin.headers["Authorization"] = "Bearer " + os.environ["XANO_METADATA_TOKEN"]
        tabelas = self.listar("/table")
        self.contas = next(t["id"] for t in tabelas if t["name"] == "conta_acesso")
        grupos = self.listar("/apigroup")
        self.grupo = next(g["id"] for g in grupos if g["name"] == "Sorriso Acesso")
        self.criadas = []

    def listar(self, caminho):
        pagina, itens = 1, []
        while pagina:
            dados = self.metadados("GET", caminho, params={"page": pagina, "per_page": 100})
            if isinstance(dados, list):
                return dados
            itens.extend(dados["items"])
            pagina = dados.get("nextPage")
        return itens

    def aguardar_limite(self):
        time.sleep(max(0, 3 - (time.monotonic() - self.ultima_chamada)))
        self.ultima_chamada = time.monotonic()

    def metadados(self, metodo, caminho, **kwargs):
        self.aguardar_limite()
        resposta = self.admin.request(metodo, self.meta + caminho, timeout=30, **kwargs)
        if resposta.status_code == 429:
            time.sleep(22)
            self.aguardar_limite()
            resposta = self.admin.request(metodo, self.meta + caminho, timeout=30, **kwargs)
        if not resposta.ok:
            pytest.fail(f"Metadados: HTTP {resposta.status_code}, operacao {metodo} {caminho}")
        return resposta.json() if resposta.content else None

    def chamar(self, metodo, rota, token=None, base=None, **kwargs):
        cabecalhos = {"Authorization": "Bearer " + token} if token else {}
        self.aguardar_limite()
        resposta = requests.request(metodo, (base or self.base) + rota,
                                    headers=cabecalhos, timeout=30, allow_redirects=False, **kwargs)
        if resposta.status_code == 429:
            time.sleep(22)
            self.aguardar_limite()
            resposta = requests.request(metodo, (base or self.base) + rota,
                                        headers=cabecalhos, timeout=30, allow_redirects=False, **kwargs)
        return resposta

    def criar(self, perfis=None, situacao="ativo"):
        senha = secrets.token_urlsafe(32)
        dados = {"nome": "Pessoa Ficticia de Verificacao",
                 "email": "verificacao." + secrets.token_hex(10) + "@example.com",
                 "senha": senha, "perfis": perfis or ["profissional"], "situacao": situacao}
        conta = self.metadados("POST", f"/table/{self.contas}/content", json=dados)
        self.criadas.append(conta["id"])
        # O campo password do Xano precisa transformar a senha antes de persistir.
        if not conta.get("senha") or conta["senha"] == senha:
            pytest.fail("A senha da conta ficticia nao foi transformada pelo backend.")
        return {"id": conta["id"], "email": dados["email"], "senha": senha}

    def alterar(self, conta, **dados):
        self.metadados("PUT", f"/table/{self.contas}/content/{conta['id']}", json=dados)

    def entrar(self, conta, esperado=200, base=None):
        resposta = self.chamar("POST", "/auth/login", base=base,
                              json={"email": conta["email"], "senha": conta["senha"]})
        exigir_status(resposta, esperado)
        return resposta.json()

    def historico(self):
        dados = self.metadados("GET", "/request_history",
                              params={"apigroup_id": self.grupo, "per_page": 100,
                                      "include_output": True})
        return dados.get("items", [])


def exigir_status(resposta, esperado):
    if resposta.status_code != esperado:
        pytest.fail(f"HTTP esperado {esperado}; recebido {resposta.status_code}")


@pytest.fixture(scope="module")
def ambiente():
    alvo = Ambiente()
    assert not alvo.historico(), "Historico de autenticacao precisa estar desativado."
    try:
        yield alvo
    finally:
        for identificador in alvo.criadas:
            alvo.metadados("PUT", f"/table/{alvo.contas}/content/{identificador}",
                           json={"situacao": "inativo"})
        alvo.admin.close()


@pytest.mark.parametrize("metodo,rota", [("GET", "/auth/me"), ("POST", "/auth/logout")])
def test_sem_autenticacao(ambiente, metodo, rota):
    exigir_status(ambiente.chamar(metodo, rota), 401)
    exigir_status(ambiente.chamar(metodo, rota, token="token-invalido"), 401)


@pytest.mark.parametrize("dados", [
    {}, {"email": "teste@example.com"}, {"senha": "ficticia"},
    {"email": "invalido", "senha": "ficticia"},
    {"email": "teste@example.com", "senha": ""},
    {"email": "teste@example.com", "senha": "ficticia", "perfil": "administrador"},
    {"email": "teste@example.com", "senha": None},
])
def test_campos_rejeitados_no_backend(ambiente, dados):
    exigir_status(ambiente.chamar("POST", "/auth/login", json=dados), 400)


@pytest.mark.parametrize("perfis,situacao,status", [
    (["administrador"], "ativo", 200),
    (["recepcionista"], "ativo", 200),
    (["profissional"], "ativo", 200),
    (["administrador", "profissional", "paciente"], "ativo", 200),
    (["paciente"], "ativo", 403),
    (["profissional"], "bloqueado", 401),
    (["profissional"], "inativo", 401),
])
def test_perfis_e_situacao(ambiente, perfis, situacao, status):
    conta = ambiente.criar(perfis, situacao)
    dados = ambiente.entrar(conta, status)
    if status == 200:
        token = dados["token"]
        assert dados["tipo_token"] == "Bearer"
        prazo = datetime.fromisoformat(dados["expira_em"].replace("Z", "+00:00"))
        assert 3500 < (prazo - datetime.now(timezone.utc)).total_seconds() <= 3600
        resposta = ambiente.chamar("GET", "/auth/me", token)
        exigir_status(resposta, 200)
        assert resposta.headers.get("Cache-Control") == "no-store"
        identidade = resposta.json()
        assert identidade["conta"] == {
            "id": conta["id"], "nome": "Pessoa Ficticia de Verificacao",
            "perfis": perfis, "situacao": "ativo",
        }
        assert identidade["expira_em"] == dados["expira_em"]
        exigir_status(ambiente.chamar("POST", "/auth/logout", token), 204)


def test_credenciais_invalidas_nao_revelam_conta(ambiente):
    conta = ambiente.criar()
    invalida = dict(conta, senha="senha-incorreta-ficticia")
    inexistente = dict(invalida, email="inexistente." + secrets.token_hex(8) + "@example.com")
    assert ambiente.entrar(invalida, 401) == ambiente.entrar(inexistente, 401)


def test_normalizacao_email_e_senha_preservada(ambiente):
    conta = ambiente.criar()
    conta["senha"] = " " + secrets.token_urlsafe(24) + " "
    ambiente.alterar(conta, senha=conta["senha"])
    conta["email"] = " " + conta["email"].upper() + " "
    token = ambiente.entrar(conta)["token"]
    exigir_status(ambiente.chamar("POST", "/auth/logout", token), 204)


def test_revogacao_idempotencia_e_sessoes_independentes(ambiente):
    conta = ambiente.criar()
    a = ambiente.entrar(conta)["token"]
    b = ambiente.entrar(conta)["token"]
    assert a != b
    resposta = ambiente.chamar("POST", "/auth/logout", a)
    exigir_status(resposta, 204)
    assert not resposta.content
    exigir_status(ambiente.chamar("GET", "/auth/me", a), 401)
    exigir_status(ambiente.chamar("POST", "/auth/logout", a), 204)
    exigir_status(ambiente.chamar("GET", "/auth/me", b), 200)
    exigir_status(ambiente.chamar("POST", "/auth/logout", b), 204)


@pytest.mark.parametrize("mudanca", [{"perfis": ["paciente"]}, {"situacao": "inativo"},
                                    {"situacao": "bloqueado"}])
def test_logout_apos_perda_de_acesso(ambiente, mudanca):
    conta = ambiente.criar()
    token = ambiente.entrar(conta)["token"]
    ambiente.alterar(conta, **mudanca)
    exigir_status(ambiente.chamar("GET", "/auth/me", token), 403)
    exigir_status(ambiente.chamar("POST", "/auth/logout", token), 204)


def test_identidade_nao_aceita_outro_titular(ambiente):
    conta = ambiente.criar()
    outra = ambiente.criar()
    token = ambiente.entrar(conta)["token"]
    resposta = ambiente.chamar("GET", "/auth/me", token,
                               params={"conta_id": outra["id"], "perfil": "administrador"})
    exigir_status(resposta, 200)
    assert resposta.json()["conta"]["id"] == conta["id"]
    assert resposta.json()["conta"]["perfis"] == ["profissional"]
    exigir_status(ambiente.chamar("POST", "/auth/logout", token), 204)


def test_expiracao_real_em_grupo_temporario(ambiente):
    # Plano sem branches: clone temporario so dos endpoints desta change.
    # A validade do token e da sessao e realmente reduzida; nao se altera o relogio.
    identificador = "teste-login-" + secrets.token_hex(6)
    nome = "Verificacao temporaria " + identificador
    grupo = ambiente.metadados("POST", "/apigroup",
                              json={"name": nome, "canonical": identificador,
                                    "description": "Teste temporario de expiracao", "swagger": False})
    base = ambiente.origem + "/api:" + identificador
    conta = ambiente.criar()
    try:
        for arquivo in Path("backend/xano/api/sorriso_acesso/auth").glob("*.xs"):
            codigo = arquivo.read_text(encoding="utf-8-sig")
            codigo = re.sub(r'^\s*guid = .*$', "", codigo, flags=re.MULTILINE)
            codigo = codigo.replace('api_group = "Sorriso Acesso"', 'api_group = "' + nome + '"')
            codigo = codigo.replace('$env|get:"AUTH_SESSION_TTL_SECONDS":3600|to_int', "8")
            ambiente.metadados("POST", f"/apigroup/{grupo['id']}/api",
                              data=codigo.encode("utf-8"),
                              headers={"Content-Type": "text/x-xanoscript"})
        dados = ambiente.entrar(conta, base=base)
        token = dados["token"]
        exigir_status(ambiente.chamar("GET", "/auth/me", token, base=base), 200)
        prazo = datetime.fromisoformat(dados["expira_em"].replace("Z", "+00:00"))
        espera = (prazo - datetime.now(timezone.utc)).total_seconds() + 2
        assert 0 < espera <= 12
        time.sleep(espera)
        exigir_status(ambiente.chamar("GET", "/auth/me", token, base=base), 401)
        exigir_status(ambiente.chamar("POST", "/auth/logout", token, base=base), 401)
        # O endpoint principal continua emitindo uma hora.
        dados = ambiente.entrar(conta)
        exigir_status(ambiente.chamar("POST", "/auth/logout", dados["token"]), 204)
    finally:
        ambiente.metadados("DELETE", f"/apigroup/{grupo['id']}")


def test_historico_sem_credenciais(ambiente):
    assert not ambiente.historico(), "O grupo de autenticacao registrou historico."
