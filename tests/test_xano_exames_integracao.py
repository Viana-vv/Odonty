"""Validação real, isolada e opt-in do fluxo de Exames no Xano.

Requer XANO_TESTAR_EXAMES=1, XANO_METADATA_BASE_URL, XANO_METADATA_TOKEN e
XANO_WORKSPACE_ID. Cria grupo, tabelas e função temporários; não toca no grupo
Sorriso Acesso nem em dados compartilhados. Apaga os objetos próprios ao final.
"""

import os
import re
import secrets
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlsplit

import pytest
import requests


pytestmark = pytest.mark.skipif(
    os.getenv("XANO_TESTAR_EXAMES") != "1",
    reason="Integração real de Exames exige ativação explícita.",
)
ROOT = Path(__file__).resolve().parents[1]


class AmbienteExames:
    def __init__(self):
        self.meta = os.environ["XANO_METADATA_BASE_URL"].rstrip("/") + "/workspace/" + os.environ["XANO_WORKSPACE_ID"]
        base = urlsplit(os.environ["XANO_METADATA_BASE_URL"])
        self.origin = f"{base.scheme}://{base.netloc}"
        self.admin = requests.Session()
        self.admin.headers["Authorization"] = "Bearer " + os.environ["XANO_METADATA_TOKEN"]
        self.ultima_chamada = 0.0
        self.intervalos = []
        self.grupo_id = None
        self.tabelas = []
        self.funcao_id = None

    def esperar(self):
        pausa = max(0, 4.05 - (time.monotonic() - self.ultima_chamada))
        if pausa:
            time.sleep(pausa)
        agora = time.monotonic()
        if self.ultima_chamada:
            self.intervalos.append(agora - self.ultima_chamada)
        self.ultima_chamada = agora

    def metadata(self, metodo, caminho, **kwargs):
        self.esperar()
        resposta = self.admin.request(metodo, self.meta + caminho, timeout=35, **kwargs)
        if resposta.status_code == 429:
            time.sleep(22)
            self.esperar()
            resposta = self.admin.request(metodo, self.meta + caminho, timeout=35, **kwargs)
        if not resposta.ok:
            try:
                corpo = resposta.json()
                detalhe = f"{corpo.get('code', corpo.get('error_code', 'erro'))}: {corpo.get('message', 'falha de metadata')}"
            except ValueError:
                detalhe = "resposta de erro sem JSON"
            segredo = getattr(self, "segredo", None)
            if segredo:
                detalhe = detalhe.replace(segredo, "[segredo temporário oculto]")
            pytest.fail(f"Metadata {metodo} {caminho}: HTTP {resposta.status_code}; {detalhe[:500]}")
        return resposta.json() if resposta.content else None

    def api(self, metodo, caminho, token=None, **kwargs):
        self.esperar()
        headers = {"Authorization": "Bearer " + token} if token else {}
        resposta = requests.request(metodo, self.base + caminho, headers=headers,
                                    timeout=35, allow_redirects=False, **kwargs)
        if resposta.status_code == 429:
            time.sleep(22)
            self.esperar()
            resposta = requests.request(metodo, self.base + caminho, headers=headers,
                                        timeout=35, allow_redirects=False, **kwargs)
        return resposta

    def upload_table(self, nome, source):
        source = re.sub(r"^\s*guid = .*?$", "", source, flags=re.MULTILINE)
        source = remap(source, self.prefix)
        result = self.metadata("POST", "/table", data=source.encode(),
                               headers={"Content-Type": "text/x-xanoscript"})
        self.tabelas.append(result["id"])
        return result["id"]

    def upload_api(self, source):
        source = re.sub(r"^\s*guid = .*?$", "", source, flags=re.MULTILINE)
        source = remap(source, self.prefix)
        source = source.replace("function.run sorriso_validar_sessao", "function.run " + self.funcao_nome)
        source = source.replace('api_group = "Sorriso Acesso"', 'api_group = "' + self.nome + '"')
        resposta = self.metadata("POST", f"/apigroup/{self.grupo_id}/api", data=source.encode(),
                                 headers={"Content-Type": "text/x-xanoscript"})
        assert resposta is not None

    def close(self):
        failures = []
        if self.grupo_id:
            try:
                self.metadata("DELETE", f"/apigroup/{self.grupo_id}")
            except Exception as exc:  # best effort cleanup; include no response body
                failures.append("grupo temporário")
        if self.funcao_id:
            try:
                self.metadata("DELETE", f"/function/{self.funcao_id}")
            except Exception:
                failures.append("função temporária")
        for table_id in reversed(self.tabelas):
            try:
                self.metadata("DELETE", f"/table/{table_id}")
            except Exception:
                failures.append("tabela temporária")
        self.admin.close()
        assert not failures, "Não foi possível confirmar a remoção de todos os objetos temporários."
        assert not self.intervalos or min(self.intervalos) >= 3.0


def remap(source, prefix):
    names = ("exame_situacao_historico", "exame_situacao_controle", "conta_acesso", "sessao_acesso", "paciente", "profissional", "consulta", "exame")
    for name in names:
        source = re.sub(rf'(\bdb\.(?:get|add|edit|query)\s+){name}\b', rf'\g<1>{prefix}{name}', source)
        source = re.sub(rf'(\b(?:auth|table)\s*=\s*"){name}(\")', rf'\g<1>{prefix}{name}\g<2>', source)
        source = re.sub(rf'(\btable\s+){name}\b', rf'\g<1>{prefix}{name}', source)
        source = re.sub(rf'(\$db\.){name}(\.)', rf'\g<1>{prefix}{name}\g<2>', source)
        source = re.sub(rf'(\bsort\s*=\s*\{{){name}(\.)', rf'\g<1>{prefix}{name}\g<2>', source)
    return source


def schema_minimo(prefix):
    schemas = {
        "conta_acesso": f'''table {prefix}conta_acesso {{
  auth = true
  schema {{
    int id
    text nome
    email email
    password senha
    enum[] perfis {{ values = ["administrador", "recepcionista", "profissional", "paciente"] }}
    enum situacao?="ativo" {{ values = ["ativo", "inativo", "bloqueado"] }}
  }}
  index = [
    {{type: "primary", field: [{{name: "id"}}]}}
    {{type: "btree|unique", field: [{{name: "email", op: "asc"}}]}}
  ]
}}''',
        "sessao_acesso": f'''table {prefix}sessao_acesso {{
  auth = false
  schema {{
    uuid id
    int conta_acesso_id {{ table = "{prefix}conta_acesso" }}
    timestamp criada_em?=now
    timestamp expira_em
    timestamp? revogada_em?
  }}
  index = [{{type: "primary", field: [{{name: "id"}}]}}]
}}''',
        "paciente": f'''table {prefix}paciente {{
  auth = false
  schema {{
    int id
    text nome
    int? conta_acesso_id? {{ table = "{prefix}conta_acesso" }}
    enum? situacao? {{ values = ["ativo", "inativo"] }}
  }}
  index = [{{type: "primary", field: [{{name: "id"}}]}}]
}}''',
        "profissional": f'''table {prefix}profissional {{
  auth = false
  schema {{
    int id
    int conta_acesso_id {{ table = "{prefix}conta_acesso" }}
    enum situacao?=Ativo {{ values = ["Ativo", "Inativo"] }}
  }}
  index = [{{type: "primary", field: [{{name: "id"}}]}}]
}}''',
        "consulta": f'''table {prefix}consulta {{
  auth = false
  schema {{
    int id
    int paciente_id {{ table = "{prefix}paciente" }}
    int profissional_id {{ table = "{prefix}profissional" }}
  }}
  index = [{{type: "primary", field: [{{name: "id"}}]}}]
}}''',
    }
    return schemas


def origem_xanoscript(relative):
    return (ROOT / relative).read_text(encoding="utf-8-sig")


@pytest.fixture
def xano_exames():
    a = AmbienteExames()
    nonce = secrets.token_hex(5)
    a.prefix = "te" + nonce + "_"
    a.nome = "teste-exames-" + nonce
    a.funcao_nome = "sorriso_validar_sessao_" + nonce
    grupo = a.metadata("POST", "/apigroup", json={
        "name": a.nome, "canonical": a.nome, "description": "Teste isolado de Exames com dados fictícios", "swagger": False,
    })
    a.grupo_id = grupo["id"]
    a.base = a.origin + "/api:" + grupo["canonical"]
    try:
        for table in schema_minimo(a.prefix).values():
            result = a.metadata("POST", "/table", data=table.encode(), headers={"Content-Type": "text/x-xanoscript"})
            a.tabelas.append(result["id"])
        for nome in ("exame", "exame_situacao_controle", "exame_situacao_historico"):
            a.upload_table(nome, origem_xanoscript(f"backend/xano/table/{nome}.xs"))
        source_funcao = origem_xanoscript("backend/xano/function/sorriso_validar_sessao.xs")
        source_funcao = re.sub(r"^\s*guid = .*?$", "", source_funcao, flags=re.MULTILINE)
        source_funcao = source_funcao.replace("function sorriso_validar_sessao", "function " + a.funcao_nome)
        funcao = a.metadata("POST", "/function", data=remap(source_funcao, a.prefix).encode(), headers={"Content-Type": "text/x-xanoscript"})
        a.funcao_id = funcao["id"]
        for route in ("auth/login_POST.xs", "exames_GET.xs", "exames_POST.xs", "exames_id_situacao_PATCH.xs"):
            a.upload_api(origem_xanoscript("backend/xano/api/sorriso_acesso/" + route))
        yield a
    finally:
        a.close()


def conta(a, table_id, nome, perfil):
    senha = secrets.token_urlsafe(24)
    email = "teste." + secrets.token_hex(8) + "@example.com"
    row = a.metadata("POST", f"/table/{table_id}/content", json={
        "nome": nome, "email": email, "senha": senha, "perfis": [perfil], "situacao": "ativo",
    })
    assert row.get("senha") and row["senha"] != senha
    assert row.get("perfis") == [perfil] and row.get("situacao") == "ativo", "A conta fictícia não preservou perfil/situação no Xano."
    response = a.api("POST", "/auth/login", json={"email": email, "senha": senha})
    body = response.json() if response.headers.get("content-type", "").startswith("application/json") else {}
    assert response.status_code == 200, f"Login fictício: HTTP {response.status_code}, código {body.get('codigo')}."
    return row["id"], response.json()["token"]


def test_exames_real_autorizacao_transicoes_historico_e_cronologia(xano_exames):
    a = xano_exames
    tables = {"conta_acesso": a.tabelas[0], "sessao_acesso": a.tabelas[1],
              "paciente": a.tabelas[2], "profissional": a.tabelas[3],
              "consulta": a.tabelas[4], "exame": a.tabelas[5],
              "exame_situacao_controle": a.tabelas[6], "exame_situacao_historico": a.tabelas[7]}
    profissional_id, token_profissional = conta(a, tables["conta_acesso"], "Profissional Fictício", "profissional")
    outro_profissional_id, token_outro = conta(a, tables["conta_acesso"], "Outro Profissional Fictício", "profissional")
    paciente_conta_id, token_paciente = conta(a, tables["conta_acesso"], "Paciente Fictício", "paciente")
    _, token_recepcao = conta(a, tables["conta_acesso"], "Recepcionista Fictícia", "recepcionista")
    _, token_profissional_sem_vinculo = conta(a, tables["conta_acesso"], "Profissional sem vínculo Fictício", "profissional")
    profissional = a.metadata("POST", f"/table/{tables['profissional']}/content", json={"conta_acesso_id": profissional_id, "situacao": "Ativo"})
    outro_profissional = a.metadata("POST", f"/table/{tables['profissional']}/content", json={"conta_acesso_id": outro_profissional_id, "situacao": "Ativo"})
    paciente = a.metadata("POST", f"/table/{tables['paciente']}/content", json={"nome": "Paciente Fictício", "conta_acesso_id": paciente_conta_id, "situacao": "ativo"})
    consulta = a.metadata("POST", f"/table/{tables['consulta']}/content", json={"paciente_id": paciente["id"], "profissional_id": profissional["id"]})
    agora = datetime.now(timezone.utc)
    solicitado = (agora - timedelta(hours=1)).isoformat()
    realizado = (agora - timedelta(minutes=5)).isoformat()
    payload = {"paciente_id": paciente["id"], "consulta_id": consulta["id"], "tipo": "Radiografia fictícia", "solicitado_em": solicitado}
    criada = a.api("POST", "/exames", token_profissional, json=payload)
    corpo_criada = criada.json() if criada.headers.get("content-type", "").startswith("application/json") else {}
    assert criada.status_code == 201, f"Solicitação de Exame: HTTP {criada.status_code}, código {corpo_criada.get('codigo')}."
    exame = criada.json()["exame"]
    assert exame["situacao"] == "Solicitado"
    assert "arquivo" not in exame and "url_publica" not in exame

    direto = a.api("PATCH", f"/exames/{exame['id']}/situacao", token_profissional, json={"situacao": "Resultado disponível", "resultado": "Resultado fictício", "realizado_em": realizado})
    assert direto.status_code == 409
    fora_de_ordem = a.api("PATCH", f"/exames/{exame['id']}/situacao", token_profissional, json={"situacao": "Realizado", "realizado_em": (agora - timedelta(hours=2)).isoformat()})
    assert fora_de_ordem.status_code == 400
    concluido = a.api("PATCH", f"/exames/{exame['id']}/situacao", token_profissional, json={"situacao": "Realizado", "realizado_em": realizado})
    assert concluido.status_code == 200
    sem_resultado = a.api("PATCH", f"/exames/{exame['id']}/situacao", token_profissional, json={"situacao": "Resultado disponível"})
    assert sem_resultado.status_code == 400
    liberado = a.api("PATCH", f"/exames/{exame['id']}/situacao", token_profissional, json={"situacao": "Resultado disponível", "resultado": "Resultado odontológico fictício"})
    assert liberado.status_code == 200
    assert liberado.json()["exame"]["resultado"] == "Resultado odontológico fictício"

    proprio = a.api("GET", "/exames", token_paciente)
    corpo_proprio = proprio.json() if proprio.headers.get("content-type", "").startswith("application/json") else {}
    detalhe_proprio = corpo_proprio.get("message", corpo_proprio.get("error", list(corpo_proprio.keys())))
    assert proprio.status_code == 200, f"Lista própria: HTTP {proprio.status_code}, código {corpo_proprio.get('codigo')}, detalhe {detalhe_proprio}."
    assert corpo_proprio["exames"][0]["resultado"] == "Resultado odontológico fictício"
    estranho = a.api("GET", "/exames", token_paciente, params={"paciente_id": paciente["id"] + 1000})
    corpo_estranho = estranho.json() if estranho.headers.get("content-type", "").startswith("application/json") else {}
    assert estranho.status_code == 404, f"Filtro fora do escopo: HTTP {estranho.status_code}, chaves {list(corpo_estranho)}."
    assert corpo_estranho.get("codigo") == "RECURSO_NAO_ENCONTRADO"
    sem_permissao = a.api("PATCH", f"/exames/{exame['id']}/situacao", token_recepcao, json={"situacao": "Cancelado"})
    assert sem_permissao.status_code == 403
    fora_escopo = a.api("PATCH", f"/exames/{exame['id']}/situacao", token_outro, json={"situacao": "Cancelado"})
    assert fora_escopo.status_code == 404
    listado_recepcao = a.api("GET", "/exames", token_recepcao)
    sem_vinculo = a.api("GET", "/exames", token_profissional_sem_vinculo)
    assert sem_vinculo.status_code == 403
    assert listado_recepcao.status_code == 403

    controle = a.metadata("GET", f"/table/{tables['exame_situacao_controle']}/content", params={"page": 1, "per_page": 100})
    controles = controle if isinstance(controle, list) else controle["items"]
    assert any(item["exame_id"] == exame["id"] and item["versao"] == 2 for item in controles)
    historico = a.metadata("GET", f"/table/{tables['exame_situacao_historico']}/content", params={"page": 1, "per_page": 100})
    rows = historico if isinstance(historico, list) else historico["items"]
    eventos = [row for row in rows if row["exame_id"] == exame["id"]]
    assert [row["situacao_nova"] for row in eventos] == ["Solicitado", "Realizado", "Resultado disponível"]
    assert [row["situacao_anterior"] for row in eventos] == [None, "Solicitado", "Realizado"]
    assert a.intervalos and min(a.intervalos) >= 3.0
