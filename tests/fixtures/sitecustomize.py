"""Backend HTTP falso opt-in para inspeção local da Agenda no navegador.

Só intercepta chamadas quando ODONTY_AGENDA_FICTICIA=1 e nunca alcança o Xano.
"""
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlsplit


if os.getenv("ODONTY_AGENDA_FICTICIA") == "1":
    import requests

    _BASE = "https://exemplo.invalid/api:agenda-ficticia"
    _FIXTURE_PATH = Path(__file__).with_name("agenda_ficticia.json")
    _FIXTURE = json.loads(_FIXTURE_PATH.read_text(encoding="utf-8"))
    _CONSULTAS = list(_FIXTURE["consultas"])
    _PERFIL = os.getenv("ODONTY_AGENDA_PERFIL", "recepcionista")
    _EXPIRACAO = (datetime.now(timezone.utc) + timedelta(hours=2)).replace(microsecond=0)

    class _RespostaFicticia:
        def __init__(self, payload=None, status=200):
            self.status_code = status
            self._payload = payload

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def json(self):
            if self._payload is None:
                raise ValueError("Sem corpo JSON.")
            return self._payload

    def _consultas_visiveis(params):
        rows = _CONSULTAS
        inicio, fim = params.get("inicio"), params.get("fim")
        if inicio and fim:
            rows = [row for row in rows if row["inicio_em"] >= inicio and row["fim_em"] <= fim]
        if params.get("profissional_id"):
            rows = [row for row in rows if row["profissional_id"] == int(params["profissional_id"])]
        if params.get("situacao"):
            rows = [row for row in rows if row["situacao"] == params["situacao"]]
        return [dict(row) for row in rows]

    def _request(method, url, *, json=None, headers=None, params=None, **_kwargs):
        if not url.startswith(_BASE + "/"):
            raise requests.ConnectionError("A API fictícia bloqueou uma chamada fora do host local de teste.")
        route = urlsplit(url).path.removeprefix(urlsplit(_BASE).path)
        if route == "/auth/login" and method == "POST":
            return _RespostaFicticia({
                "token": "token-local-ficticio", "tipo_token": "Bearer",
                "expira_em": _EXPIRACAO.isoformat().replace("+00:00", "Z"),
            })
        if route == "/auth/me" and method == "GET":
            return _RespostaFicticia({"conta": {
                "id": 77, "nome": "Equipe Fictícia Agenda", "perfis": [_PERFIL], "situacao": "ativo",
            }, "expira_em": _EXPIRACAO.isoformat().replace("+00:00", "Z")})
        if route == "/auth/logout" and method == "POST":
            return _RespostaFicticia(status=204)
        if not headers or headers.get("Authorization") != "Bearer token-local-ficticio":
            return _RespostaFicticia({"codigo": "ACESSO_NEGADO"}, 401)
        if route == "/agenda/opcoes" and method == "GET":
            return _RespostaFicticia(_FIXTURE["opcoes"])
        if route == "/consultas" and method == "GET":
            return _RespostaFicticia({"consultas": _consultas_visiveis(params or {})})
        if route == "/disponibilidades" and method == "GET":
            inicio, fim = (params or {}).get("inicio"), (params or {}).get("fim")
            inicio_dt = datetime.fromisoformat(inicio.replace("Z", "+00:00")) if inicio else None
            fim_dt = datetime.fromisoformat(fim.replace("Z", "+00:00")) if fim else None
            rows = [d for d in _FIXTURE["disponibilidades"]
                    if d["profissional_id"] == int((params or {}).get("profissional_id", d["profissional_id"]))
                    and (not inicio_dt or datetime.fromisoformat(d["inicio"].replace("Z", "+00:00")) >= inicio_dt)
                    and (not fim_dt or datetime.fromisoformat(d["fim"].replace("Z", "+00:00")) <= fim_dt)]
            return _RespostaFicticia({"disponibilidades": [dict(row) for row in rows]})
        if route == "/consultas" and method == "POST":
            dados = json or {}
            slot = next((d for d in _FIXTURE["disponibilidades"] if d["id"] == dados.get("disponibilidade_id")), None)
            paciente = next((p for p in _FIXTURE["opcoes"]["pacientes"] if p["id"] == dados.get("paciente_id")), None)
            profissional = next((p for p in _FIXTURE["opcoes"]["profissionais"] if slot and p["id"] == slot["profissional_id"]), None)
            if not slot or not paciente or not profissional:
                return _RespostaFicticia({"codigo": "DADOS_INVALIDOS"}, 400)
            consulta = {
                "id": 503, "paciente_id": paciente["id"], "profissional_id": profissional["id"],
                "disponibilidade_id": slot["id"], "situacao": "Agendada", "inicio_em": slot["inicio"],
                "fim_em": slot["fim"], "paciente_nome": paciente["nome"], "profissional_nome": profissional["nome"],
                "procedimento_nome": None, "procedimento_vinculado_nome": None,
            }
            nomes = [p["nome"] for p in _FIXTURE["opcoes"]["procedimentos"] if p["id"] in dados.get("procedimento_ids", [])]
            if not nomes:
                _CONSULTAS.append(dict(consulta))
            else:
                consulta["procedimento_nome"] = nomes[0]
                for nome in nomes:
                    _CONSULTAS.append(dict(consulta, procedimento_vinculado_nome=nome))
            return _RespostaFicticia({"consulta": {
                "id": consulta["id"], "paciente_id": consulta["paciente_id"],
                "profissional_id": consulta["profissional_id"], "disponibilidade_id": consulta["disponibilidade_id"],
                "situacao": consulta["situacao"],
            }}, 201)
        if route.startswith("/consultas/") and route.endswith("/situacao") and method == "PATCH":
            consulta_id = int(route.split("/")[2])
            dados = json or {}
            consulta = next((c for c in _CONSULTAS if c["id"] == consulta_id), None)
            if not consulta:
                return _RespostaFicticia({"codigo": "RECURSO_NAO_ENCONTRADO"}, 404)
            for row in _CONSULTAS:
                if row["id"] == consulta_id:
                    row["situacao"] = dados.get("situacao", row["situacao"])
            return _RespostaFicticia({"consulta": {
                "id": consulta_id, "paciente_id": consulta["paciente_id"],
                "profissional_id": consulta["profissional_id"],
                "disponibilidade_id": consulta.get("disponibilidade_id"), "situacao": dados.get("situacao"),
            }})
        return _RespostaFicticia({"codigo": "RECURSO_NAO_ENCONTRADO"}, 404)

    requests.request = _request
