"""Contrato REST do Xano. Nunca registra payloads ou credenciais."""

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone

import requests

from .config import Configuracao

ROTULOS = {"administrador": "Administrador", "recepcionista": "Recepcionista", "profissional": "Dentista"}
PERFIS_DOMINIO = set(ROTULOS) | {"paciente"}
INDISPONIVEL = "Não foi possível conectar ao serviço. Tente novamente em instantes."


class ErroAcesso(Exception):
    def __init__(self, mensagem=INDISPONIVEL, status=None):
        super().__init__(mensagem)
        self.status = status


@dataclass(frozen=True)
class Credencial:
    token: str = field(repr=False)
    expira_em: datetime


@dataclass(frozen=True)
class ContaAcesso:
    id: int
    nome: str
    perfis: tuple[str, ...]
    expira_em: datetime


def validar_campos(email, senha):
    email = email.strip().lower()
    if not email or not senha:
        raise ErroAcesso("Preencha o e-mail e a senha.", 400)
    if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
        raise ErroAcesso("Informe um e-mail válido.", 400)
    return email


def ler_validade(value):
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|\+00:00)", value):
        raise ErroAcesso()
    try:
        expiration = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        raise ErroAcesso() from None
    if expiration <= datetime.now(timezone.utc):
        raise ErroAcesso("Sua sessão expirou. Entre novamente.", 401)
    return expiration


class ClienteXano:
    def __init__(self, configuracao: Configuracao):
        self.configuracao = configuracao

    def _request(self, method, route, token=None, payload=None):
        headers = {"Accept": "application/json"}
        if token:
            if not isinstance(token, str) or any(c.isspace() for c in token):
                raise ErroAcesso("Sua sessão não é válida. Entre novamente.", 401)
            headers["Authorization"] = f"Bearer {token}"
        try:
            response = requests.request(
                method, self.configuracao.api_base_url + route,
                json=payload, headers=headers, timeout=self.configuracao.timeout,
                allow_redirects=False,
            )
        except requests.RequestException:
            raise ErroAcesso() from None
        with response:
            status = response.status_code
            if route == "/auth/logout" and status in (204, 401):
                return None
            if status != 200:
                messages = {
                    400: "Confira os dados informados e tente novamente.",
                    401: ("E-mail ou senha incorretos, ou conta indisponível."
                          if route == "/auth/login" else "Sua sessão expirou ou não é válida. Entre novamente."),
                    403: "Sua conta não tem permissão para acessar esta área.",
                    429: "Muitas tentativas. Aguarde um pouco antes de tentar novamente.",
                }
                raise ErroAcesso(messages.get(status, INDISPONIVEL), status)
            try:
                data = response.json()
            except ValueError:
                raise ErroAcesso() from None
            if not isinstance(data, dict):
                raise ErroAcesso()
            return data

    def entrar(self, email, senha):
        email = validar_campos(email, senha)
        data = self._request("POST", "/auth/login", payload={"email": email, "senha": senha})
        token = data.get("token")
        if (not isinstance(token, str) or not token or any(c.isspace() for c in token)
                or data.get("tipo_token") != "Bearer"):
            raise ErroAcesso()
        return Credencial(token, ler_validade(data.get("expira_em")))

    def identificar(self, token):
        data = self._request("GET", "/auth/me", token=token)
        account = data.get("conta")
        if not isinstance(account, dict):
            raise ErroAcesso()
        profiles = account.get("perfis")
        if (type(account.get("id")) is not int or account["id"] <= 0
                or not isinstance(account.get("nome"), str) or not account["nome"].strip()
                or not isinstance(profiles, list) or not profiles
                or any(not isinstance(p, str) or p not in PERFIS_DOMINIO for p in profiles)
                or len(set(profiles)) != len(profiles)):
            raise ErroAcesso()
        if account.get("situacao") != "ativo" or not set(profiles).intersection(ROTULOS):
            raise ErroAcesso("Sua conta não tem permissão para acessar esta área.", 403)
        return ContaAcesso(account["id"], account["nome"], tuple(p for p in ROTULOS if p in profiles), ler_validade(data.get("expira_em")))

    def sair(self, token):
        self._request("POST", "/auth/logout", token=token)
