"""Validação opt-in de Procedimentos em grupo Xano temporário e fictício."""

import os
import re
import secrets
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from urllib.parse import urlsplit

import pytest
import requests


pytestmark = pytest.mark.skipif(
    os.getenv("XANO_TESTAR_PROCEDIMENTOS") != "1",
    reason="Integração real de Procedimentos exige ativação explícita.",
)
ROOT = Path(__file__).resolve().parents[1]


class AmbienteProcedimentos:
    def __init__(self):
        self.meta = os.environ["XANO_METADATA_BASE_URL"].rstrip("/") + "/workspace/" + os.environ["XANO_WORKSPACE_ID"]
        parsed = urlsplit(os.environ["XANO_METADATA_BASE_URL"])
        self.origin = f"{parsed.scheme}://{parsed.netloc}"
        self.admin = requests.Session()
        self.admin.headers["Authorization"] = "Bearer " + os.environ["XANO_METADATA_TOKEN"]
        self.last_call = 0.0
        self.intervals = []
        self.rate_lock = threading.Lock()
        self.group_id = self.function_id = None
        self.tables = []

    def wait_rate_limit(self):
        with self.rate_lock:
            pause = max(0, 4.05 - (time.monotonic() - self.last_call))
            if pause:
                time.sleep(pause)
            now = time.monotonic()
            if self.last_call:
                self.intervals.append(now - self.last_call)
            self.last_call = now

    def metadata(self, method, path, **kwargs):
        self.wait_rate_limit()
        response = self.admin.request(method, self.meta + path, timeout=60, **kwargs)
        if response.status_code == 429:
            time.sleep(22)
            self.wait_rate_limit()
            response = self.admin.request(method, self.meta + path, timeout=60, **kwargs)
        if not response.ok:
            try:
                body = response.json()
                detail = f"{body.get('code', 'erro')}: {body.get('message', 'falha Xano')}"
            except ValueError:
                detail = "resposta sem JSON"
            pytest.fail(f"Metadata {method} {path}: HTTP {response.status_code}; {detail[:300]}")
        return response.json() if response.content else None

    def api(self, method, path, token=None, **kwargs):
        self.wait_rate_limit()
        headers = {"Authorization": "Bearer " + token} if token else {}
        api_path = path if path.startswith("/") else "/" + path
        response = requests.request(method, self.base + api_path, headers=headers, timeout=45,
                                    allow_redirects=False, **kwargs)
        if response.status_code == 429:
            time.sleep(22)
            self.wait_rate_limit()
            response = requests.request(method, self.base + api_path, headers=headers, timeout=45,
                                        allow_redirects=False, **kwargs)
        return response

    def close(self):
        failures = []
        if self.group_id:
            try:
                self.metadata("DELETE", f"/apigroup/{self.group_id}")
            except Exception:
                failures.append("grupo temporário")
        if self.function_id:
            try:
                self.metadata("DELETE", f"/function/{self.function_id}")
            except Exception:
                failures.append("função temporária")
        for table_id in reversed(self.tables):
            try:
                self.metadata("DELETE", f"/table/{table_id}")
            except Exception:
                failures.append("tabela temporária")
        self.admin.close()
        assert not failures, "Não foi confirmada a remoção de todos os objetos Xano temporários."
        assert not self.intervals or min(self.intervals) >= 3.0


def remap(source, prefix):
    names = ("conta_acesso", "sessao_acesso", "paciente", "profissional", "procedimento", "consulta", "consulta_procedimento", "agenda_controle")
    for name in names:
        source = re.sub(rf'(\bdb\.(?:get|add|edit|query)\s+){name}\b', rf'\g<1>{prefix}{name}', source)
        source = re.sub(rf'(\b(?:auth|table)\s*=\s*"){name}(\")', rf'\g<1>{prefix}{name}\g<2>', source)
        source = re.sub(rf'(\btable\s+){name}\b', rf'\g<1>{prefix}{name}', source)
        source = re.sub(rf'(\$db\.){name}(\.)', rf'\g<1>{prefix}{name}\g<2>', source)
        source = re.sub(rf'(\bsort\s*=\s*\{{){name}(\.)', rf'\g<1>{prefix}{name}\g<2>', source)
    return source


def source(relative):
    return (ROOT / relative).read_text(encoding="utf-8-sig")


def minimal_tables(prefix):
    return [
        f'''table {prefix}conta_acesso {{
  auth = true
  schema {{
    int id
    text nome
    email email
    password senha
    enum[] perfis {{
      values = ["administrador", "recepcionista", "profissional", "paciente"]
    }}
    enum situacao?="ativo" {{
      values = ["ativo", "inativo", "bloqueado"]
    }}
  }}
  index = [
    {{type: "primary", field: [{{name: "id"}}]}}
    {{type: "btree|unique", field: [{{name: "email", op: "asc"}}]}}
  ]
}}''',
        f'''table {prefix}sessao_acesso {{
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
        f'''table {prefix}paciente {{
  auth = false
  schema {{
    int id
    text nome
  }}
  index = [{{type: "primary", field: [{{name: "id"}}]}}]
}}''',
        f'''table {prefix}profissional {{
  auth = false
  schema {{
    int id
    text nome
    int conta_acesso_id {{ table = "{prefix}conta_acesso" }}
    enum situacao?=Ativo {{
      values = ["Ativo", "Inativo"]
    }}
  }}
  index = [{{type: "primary", field: [{{name: "id"}}]}}]
}}''',
        f'''table {prefix}procedimento {{
  auth = false
  schema {{
    int id
    text nome
    bool ativo?=true
  }}
  index = [{{type: "primary", field: [{{name: "id"}}]}}]
}}''',
        f'''table {prefix}consulta {{
  auth = false
  schema {{
    int id
    int paciente_id {{ table = "{prefix}paciente" }}
    int profissional_id {{ table = "{prefix}profissional" }}
    int? procedimento_id? {{ table = "{prefix}procedimento" }}
    timestamp inicio_em?=now
  }}
  index = [{{type: "primary", field: [{{name: "id"}}]}}]
}}''',
        f'''table {prefix}agenda_controle {{
  auth = false
  schema {{
    int id
    enum escopo {{ values = ["profissional", "paciente"] }}
    int escopo_id
    int versao?=0
    timestamp atualizado_em?=now
  }}
  index = [
    {{type: "primary", field: [{{name: "id"}}]}}
    {{type: "btree|unique", field: [{{name: "escopo", op: "asc"}}, {{name: "escopo_id", op: "asc"}}]}}
  ]
}}''',
    ]


@pytest.fixture
def xano_procedimentos():
    a = AmbienteProcedimentos()
    suffix = secrets.token_hex(5)
    a.prefix = "tp" + suffix + "_"
    a.name = "teste-procedimentos-" + suffix
    a.function_name = "sorriso_validar_sessao_" + suffix
    group = a.metadata("POST", "/apigroup", json={"name": a.name, "canonical": a.name,
                                                   "description": "Teste temporário com dados fictícios", "swagger": False})
    a.group_id = group["id"]
    a.base = a.origin + "/api:" + group["canonical"]
    try:
        for table in minimal_tables(a.prefix) + [remap(source("backend/xano/table/consulta_procedimento.xs"), a.prefix)]:
            table = re.sub(r"^\s*guid = .*?$", "", table, flags=re.MULTILINE)
            result = a.metadata("POST", "/table", data=table.encode(), headers={"Content-Type": "text/x-xanoscript"})
            a.tables.append(result["id"])
        func = re.sub(r"^\s*guid = .*?$", "", source("backend/xano/function/sorriso_validar_sessao.xs"), flags=re.MULTILINE)
        func = func.replace("function sorriso_validar_sessao", "function " + a.function_name)
        func = remap(func, a.prefix)
        created = a.metadata("POST", "/function", data=func.encode(), headers={"Content-Type": "text/x-xanoscript"})
        a.function_id = created["id"]
        for route in ("auth/login_POST.xs", "consultas_id_procedimentos_GET.xs", "consultas_id_procedimentos_consulta_procedimento_id_realizacao_PATCH.xs"):
            route_source = re.sub(r"^\s*guid = .*?$", "", source("backend/xano/api/sorriso_acesso/" + route), flags=re.MULTILINE)
            route_source = remap(route_source, a.prefix)
            route_source = route_source.replace("function.run sorriso_validar_sessao", "function.run " + a.function_name)
            route_source = route_source.replace('api_group = "Sorriso Acesso"', 'api_group = "' + a.name + '"')
            created = a.metadata("POST", f"/apigroup/{a.group_id}/api", data=route_source.encode(), headers={"Content-Type": "text/x-xanoscript"})
            if "procedimentos_GET" in route:
                a.get_route_metadata = {key: created.get(key) for key in ("id", "name", "route", "verb", "method", "endpoint") if key in created}
        patch_source = source("backend/xano/api/sorriso_acesso/consultas_id_procedimentos_consulta_procedimento_id_realizacao_PATCH.xs")
        patch_source = patch_source.replace('query "consultas/{id}/procedimentos/{consulta_procedimento_id}/realizacao"',
                                            'query "consultas/{id}/procedimentos/{consulta_procedimento_id}/realizacao_lenta"')
        marker = '''            db.get consulta_procedimento {
              field_name = "id"
              field_value = $vinculo.id'''
        assert patch_source.count(marker) == 1
        patch_source = patch_source.replace(marker, '            util.sleep { value = 9 }\n' + marker)
        patch_source = re.sub(r"^\\s*guid = .*?$", "", patch_source, flags=re.MULTILINE)
        patch_source = remap(patch_source, a.prefix)
        patch_source = patch_source.replace("function.run sorriso_validar_sessao", "function.run " + a.function_name)
        patch_source = patch_source.replace('api_group = "Sorriso Acesso"', 'api_group = "' + a.name + '"')
        a.metadata("POST", f"/apigroup/{a.group_id}/api", data=patch_source.encode(), headers={"Content-Type": "text/x-xanoscript"})
        probe = a.api("GET", "consultas/1/procedimentos")
        assert probe.status_code in {401, 403}, (
            f"Rota GET não registrada no grupo temporário: HTTP {probe.status_code}, "
            f"rota {getattr(a, 'get_route_metadata', {})}."
        )
        yield a
    finally:
        a.close()


def account(a, accounts_table, name, role):
    password = secrets.token_urlsafe(24)
    email = "fixture." + secrets.token_hex(8) + "@example.com"
    row = a.metadata("POST", f"/table/{accounts_table}/content", json={"nome": name, "email": email,
                                                                         "senha": password, "perfis": [role], "situacao": "ativo"})
    assert row.get("senha") and row["senha"] != password
    login = a.api("POST", "/auth/login", json={"email": email, "senha": password})
    assert login.status_code == 200
    return row["id"], login.json()["token"]


def test_procedimentos_real_xano_migration_autorizacao_e_realizacao(xano_procedimentos):
    a = xano_procedimentos
    tables = {"conta_acesso": a.tables[0], "paciente": a.tables[2], "profissional": a.tables[3],
              "procedimento": a.tables[4], "consulta": a.tables[5], "agenda_controle": a.tables[6],
              "consulta_procedimento": a.tables[7]}
    prof_id, token_prof = account(a, tables["conta_acesso"], "Profissional fictício", "profissional")
    other_prof_id, token_other = account(a, tables["conta_acesso"], "Outro profissional fictício", "profissional")
    _, token_reception = account(a, tables["conta_acesso"], "Recepcionista fictícia", "recepcionista")
    prof = a.metadata("POST", f"/table/{tables['profissional']}/content", json={"nome": "Profissional fictício", "conta_acesso_id": prof_id, "situacao": "Ativo"})
    other_prof = a.metadata("POST", f"/table/{tables['profissional']}/content", json={"nome": "Outro profissional fictício", "conta_acesso_id": other_prof_id, "situacao": "Ativo"})
    patient = a.metadata("POST", f"/table/{tables['paciente']}/content", json={"nome": "Paciente fictício"})
    procedure = a.metadata("POST", f"/table/{tables['procedimento']}/content", json={"nome": "Profilaxia fictícia", "ativo": True})
    concurrent_procedure = a.metadata("POST", f"/table/{tables['procedimento']}/content", json={"nome": "Restauração fictícia", "ativo": True})
    consultation = a.metadata("POST", f"/table/{tables['consulta']}/content", json={"paciente_id": patient["id"], "profissional_id": prof["id"]})
    other_consultation = a.metadata("POST", f"/table/{tables['consulta']}/content", json={"paciente_id": patient["id"], "profissional_id": other_prof["id"]})
    created_at = "2026-10-24T12:00:00Z"
    legacy = a.metadata("POST", f"/table/{tables['consulta_procedimento']}/content", json={"consulta_id": consultation["id"], "procedimento_id": procedure["id"], "profissional_id": prof["id"], "criado_em": created_at})
    other_link = a.metadata("POST", f"/table/{tables['consulta_procedimento']}/content", json={"consulta_id": other_consultation["id"], "procedimento_id": procedure["id"], "profissional_id": other_prof["id"], "criado_em": created_at})
    concurrent_link = a.metadata("POST", f"/table/{tables['consulta_procedimento']}/content", json={"consulta_id": consultation["id"], "procedimento_id": concurrent_procedure["id"], "profissional_id": prof["id"], "criado_em": created_at})
    assert legacy["situacao"] == "planejado" and legacy.get("realizado_por_profissional_id") is None and legacy.get("realizado_em") is None

    listed = a.api("GET", f"consultas/{consultation['id']}/procedimentos", token_prof)
    listed_body = listed.json() if listed.headers.get("content-type", "").startswith("application/json") else {}
    assert listed.status_code == 200, f"GET da Consulta: HTTP {listed.status_code}, código {listed_body.get('codigo') or listed_body.get('code')}, mensagem {listed_body.get('mensagem') or listed_body.get('message')}."
    assert listed_body["procedimentos"][0]["situacao"] == "planejado"
    assert listed.json()["procedimentos"][0]["profissional_id"] == prof["id"]
    denied_list = a.api("GET", f"consultas/{consultation['id']}/procedimentos", token_reception)
    assert denied_list.status_code == 403
    hidden_list = a.api("GET", f"consultas/{consultation['id']}/procedimentos", token_other)
    assert hidden_list.status_code == 404

    patch_path = f"consultas/{consultation['id']}/procedimentos/{legacy['id']}/realizacao"
    completed = a.api("PATCH", patch_path, token_prof, json={})
    assert completed.status_code == 200
    item = completed.json()["procedimento"]
    stored = a.metadata("GET", f"/table/{tables['consulta_procedimento']}/content/{legacy['id']}")
    assert stored.get("realizado_por_profissional_id") == prof["id"] and stored.get("realizado_em"), (
        f"Persistência da realização incompleta; campos armazenados: {list(stored)}."
    )
    assert item["situacao"] == "realizado" and item["profissional_id"] == prof["id"]
    assert item.get("realizado_por_nome") == prof["nome"] and item.get("realizado_em"), (
        f"Resposta PATCH sem autoria/data visíveis; chaves {list(item)}, campos persistidos {list(stored)}."
    )
    assert datetime.fromisoformat(item["criado_em"].replace("Z", "+00:00")) == datetime.fromisoformat(created_at.replace("Z", "+00:00"))
    duplicate = a.api("PATCH", patch_path, token_prof, json={})
    assert duplicate.status_code == 409
    foreign = a.api("PATCH", f"consultas/{consultation['id']}/procedimentos/{other_link['id']}/realizacao", token_prof, json={})
    assert foreign.status_code == 404
    forbidden = a.api("PATCH", patch_path, token_reception, json={})
    assert forbidden.status_code == 403
    after = a.api("GET", f"consultas/{consultation['id']}/procedimentos", token_prof)
    assert after.status_code == 200
    done = next(p for p in after.json()["procedimentos"] if p["id"] == legacy["id"])
    assert done["situacao"] == "realizado" and done["realizado_por_profissional_id"] == prof["id"]
    assert done["realizado_por_nome"] == prof["nome"] and done["realizado_em"]
    concurrent_path = f"consultas/{consultation['id']}/procedimentos/{concurrent_link['id']}/realizacao_lenta"
    with ThreadPoolExecutor(max_workers=2) as pool:
        first = pool.submit(a.api, "PATCH", concurrent_path, token_prof, json={})
        second = pool.submit(a.api, "PATCH", concurrent_path, token_prof, json={})
        results = [first.result(), second.result()]
    assert sorted(response.status_code for response in results) == [200, 409]
    concurrent_after = a.api("GET", f"consultas/{consultation['id']}/procedimentos", token_prof)
    concurrent_done = next(p for p in concurrent_after.json()["procedimentos"] if p["id"] == concurrent_link["id"])
    assert concurrent_done["situacao"] == "realizado" and concurrent_done["realizado_por_profissional_id"] == prof["id"]
    assert concurrent_done["realizado_em"] and concurrent_done["realizado_por_nome"] == prof["nome"]
    controls = a.metadata("GET", f"/table/{tables['agenda_controle']}/content", params={"per_page": 100})
    professional_controls = [row for row in controls if row.get("escopo") == "profissional" and row.get("escopo_id") == prof["id"]]
    assert len(professional_controls) == 1 and professional_controls[0]["versao"] >= 2
    assert a.intervals and min(a.intervals) >= 3.0
