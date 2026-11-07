"""Referência executável OFFLINE dos contratos, exclusivamente com dados fictícios.

Não é servidor, rota implantável ou substituto do Xano. Não tem rede, sender ou
acesso a contas reais. RLock e rollback abaixo provam apenas o modelo em memória;
não comprovam atomicidade, timeout de transporte, login ou compatibilidade OTP
remotos. Novas reservas ficam desabilitadas por padrão. Token bruto é entregue
somente à fábrica injetada pelo teste, nunca nas respostas administrativas.
"""
from __future__ import annotations

import base64
import copy
import hashlib
import math
import re
import secrets
import threading
from datetime import datetime, timedelta, timezone
from typing import Callable

from sorrisomais.uuid7 import instante_uuid7


class ErroContrato(Exception):
    """Erro sanitizado; o adaptador de teste pode mapear status e cabeçalhos."""

    def __init__(self, codigo: str, status: int, retry_after: int | None = None):
        self.codigo, self.status, self.retry_after = codigo, status, retry_after
        self.mensagem = "Solicitação não disponível."
        self.headers = {"Cache-Control": "no-store"}
        if retry_after is not None:
            self.headers["Retry-After"] = str(retry_after)
        super().__init__(codigo)


def _hash(valor: str) -> str:
    return hashlib.sha256(valor.encode("utf-8")).hexdigest()


def _data(valor: datetime) -> str:
    return valor.astimezone(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _id_operacao(valor: str) -> datetime:
    try:
        return instante_uuid7(valor)
    except (ValueError, TypeError, AttributeError, OverflowError):
        raise ErroContrato("DADOS_INVALIDOS", 400) from None


class BackendLocalRelogio:
    """Modelo em memória opt-in; relógio e segredos podem ser controlados em testes.

    contas: {id: {email, situacao, perfis, versao_credencial?, senha_hash?}}.
    sessoes: {id: {conta_acesso_id, expira_em: datetime, revogada_em?,
                  versao_credencial?}}. Fixtures só devem conter dados fictícios.
    antes_commit é ponto de falha local para comprovar rollback, sem argumentos.
    """

    def __init__(self, agora: Callable[[], datetime] | None = None, *,
                 habilitado: bool = False, timeout_envio_segundos: int = 20,
                 emitir_token: Callable[[], str] | None = None,
                 antes_commit: Callable[[], None] | None = None):
        self.agora = agora or (lambda: datetime.now(timezone.utc))
        self.habilitado = habilitado
        self.timeout_envio_segundos = timeout_envio_segundos
        self.emitir_token = emitir_token or (lambda: secrets.token_urlsafe(32))
        self.antes_commit = antes_commit
        self.contas: dict = {}
        self.sessoes: dict = {}
        self.operacoes: dict = {}
        self.auditoria: list = []
        self.tentativas: dict = {}
        self._lock = threading.RLock()

    def _agora(self):
        valor = self.agora()
        if valor.tzinfo is None:
            raise ValueError("Relógio de teste deve possuir timezone.")
        return valor.astimezone(timezone.utc)

    def _autorizar(self, sessao_id, agora):
        sessao = self.sessoes.get(sessao_id)
        if not sessao or sessao.get("revogada_em") or agora >= sessao["expira_em"]:
            raise ErroContrato("SESSAO_INVALIDA", 401)
        conta = self.contas.get(sessao["conta_acesso_id"])
        if not conta or sessao.get("versao_credencial", 1) != conta.get("versao_credencial", 1):
            raise ErroContrato("SESSAO_INVALIDA", 401)
        if conta["situacao"] != "ativo" or "administrador" not in conta["perfis"]:
            raise ErroContrato("ACESSO_NEGADO", 403)
        return sessao["conta_acesso_id"]

    @staticmethod
    def _conta_id(conta_id):
        if type(conta_id) is not int or conta_id <= 0:
            raise ErroContrato("DADOS_INVALIDOS", 400)

    @staticmethod
    def _codigo(codigo):
        if not isinstance(codigo, str) or not re.fullmatch(r"[A-Za-z0-9_-]{43}", codigo):
            raise ErroContrato("LINK_INDISPONIVEL", 400)
        bruto = base64.urlsafe_b64decode(codigo + "=")
        if len(bruto) != 32 or base64.urlsafe_b64encode(bruto).decode().rstrip("=") != codigo:
            raise ErroContrato("LINK_INDISPONIVEL", 400)

    @staticmethod
    def _estados(op, agora):
        envio = op["resultado_envio"]
        if envio == "processando" and agora >= op["envio_limite_em"]:
            envio = "desconhecido"
        terminal = op.get("terminal")
        link = terminal or ("expirado" if agora >= op["expira_em"] else
                            "pendente" if envio == "processando" else "ativo")
        return envio, link

    def _projetar(self, op, agora):
        envio, link = self._estados(op, agora)
        return {"operacao_id": op["operacao_id"],
                **{campo: _data(op[campo]) for campo in
                   ("criada_em", "consultavel_ate", "expira_em", "envio_limite_em")},
                "estado_envio": envio, "estado_link": link}

    def _terminal(self, op, evento, agora):
        if self._estados(op, agora)[1] in ("ativo", "pendente"):
            op.update(terminal=evento, terminal_em=agora)

    def criar(self, sessao_id, conta_id: int, operacao_id: str) -> dict:
        """POST administrativo simulado; reserva apenas, sem envio real."""
        with self._lock:
            agora = self._agora()
            solicitante = self._autorizar(sessao_id, agora)
            self._conta_id(conta_id)
            instante_id = _id_operacao(operacao_id)
            anterior = self.operacoes.get(operacao_id)
            if anterior:
                if agora >= anterior["consultavel_ate"]:
                    raise ErroContrato("OPERACAO_ANTIGA", 409)
                if (anterior["solicitante_id"], anterior["conta_id"]) != (solicitante, conta_id):
                    raise ErroContrato("OPERACAO_CONFLITANTE", 409)
                return self._projetar(anterior, agora)
            if instante_id < agora - timedelta(minutes=5):
                raise ErroContrato("OPERACAO_ANTIGA", 409)
            if instante_id > agora + timedelta(seconds=60):
                raise ErroContrato("OPERACAO_FUTURA", 409)
            conta = self.contas.get(conta_id)
            if not conta:
                raise ErroContrato("CONTA_NAO_ENCONTRADA", 404)
            if conta["situacao"] != "ativo":
                raise ErroContrato("CONTA_INELEGIVEL", 409)
            if self.habilitado is not True or type(self.timeout_envio_segundos) is not int or not 1 <= self.timeout_envio_segundos <= 30:
                raise ErroContrato("RECURSO_INDISPONIVEL", 503)
            recentes = [op for op in self.operacoes.values() if op["criada_em"] > agora - timedelta(hours=1)]
            esperas = []
            for campo, valor, limite in (("solicitante_id", solicitante, 10), ("conta_id", conta_id, 3)):
                datas = sorted(op["criada_em"] for op in recentes if op[campo] == valor)
                if len(datas) >= limite:
                    esperas.append((datas[-limite] + timedelta(hours=1) - agora).total_seconds())
            datas = [op["criada_em"] for op in recentes if op["conta_id"] == conta_id]
            if datas and agora < max(datas) + timedelta(seconds=60):
                esperas.append((max(datas) + timedelta(seconds=60) - agora).total_seconds())
            if esperas:
                raise ErroContrato("LIMITE_ENVIO", 429, max(1, math.ceil(max(esperas))))
            token = self.emitir_token()
            self._codigo(token)
            token_hash = _hash(token)
            if any(op["token_hash"] == token_hash for op in self.operacoes.values()):
                raise ErroContrato("SERVICO_INDISPONIVEL", 503)
            op = dict(operacao_id=operacao_id, solicitante_id=solicitante, conta_id=conta_id,
                      email_hash=_hash(conta["email"].strip().lower()),
                      versao_credencial=conta.get("versao_credencial", 1), token_hash=token_hash,
                      criada_em=agora, consultavel_ate=agora + timedelta(days=30),
                      expira_em=agora + timedelta(minutes=15),
                      envio_limite_em=agora + timedelta(seconds=self.timeout_envio_segundos),
                      resultado_envio="processando", terminal=None)
            for antiga in self.operacoes.values():
                if antiga["conta_id"] == conta_id:
                    self._terminal(antiga, "substituido", agora)
            self.operacoes[operacao_id] = op
            self.auditoria.append(dict(operacao_id=operacao_id, solicitante_id=solicitante,
                                      conta_id=conta_id, data=agora, resultado="reservada"))
            return self._projetar(op, agora)

    def consultar(self, sessao_id, conta_id: int, operacao_id: str) -> dict:
        """GET estritamente somente leitura, inclusive prazos vencidos."""
        with self._lock:
            agora = self._agora()
            solicitante = self._autorizar(sessao_id, agora)
            self._conta_id(conta_id)
            _id_operacao(operacao_id)
            op = self.operacoes.get(operacao_id)
            if not op or agora >= op["consultavel_ate"] or (op["solicitante_id"], op["conta_id"]) != (solicitante, conta_id):
                raise ErroContrato("OPERACAO_NAO_ENCONTRADA", 404)
            return self._projetar(op, agora)

    def registrar_resultado(self, operacao_id: str, estado_envio: str) -> None:
        """Simula evidência de transporte; jamais chama um provedor."""
        if estado_envio not in ("aceito", "falhou", "desconhecido"):
            raise ValueError("Resultado de teste inválido.")
        with self._lock:
            op = self.operacoes[operacao_id]
            if op["resultado_envio"] in ("aceito", "falhou"):
                return
            op["resultado_envio"] = estado_envio
            if estado_envio == "falhou":
                self._terminal(op, "invalidado", self._agora())

    def confirmar(self, codigo: str, nova_senha: str) -> None:
        """POST público simulado; None representa 204, sem login automático."""
        self._codigo(codigo)
        with self._lock:
            agora = self._agora()
            token_hash = _hash(codigo)
            tentativas = [data for data in self.tentativas.get(token_hash, []) if data > agora - timedelta(minutes=15)]
            if len(tentativas) >= 30:
                raise ErroContrato("LIMITE_CONFIRMACAO", 429, max(1, math.ceil((tentativas[0] + timedelta(minutes=15) - agora).total_seconds())))
            self.tentativas[token_hash] = tentativas + [agora]
            if not isinstance(nova_senha, str) or not 12 <= len(nova_senha) <= 128:
                raise ErroContrato("DADOS_INVALIDOS", 400)
            op = next((op for op in self.operacoes.values() if op["token_hash"] == token_hash), None)
            conta = self.contas.get(op["conta_id"]) if op else None
            if not conta or self._estados(op, agora)[1] not in ("pendente", "ativo") or conta["situacao"] != "ativo" or conta.get("versao_credencial", 1) != op["versao_credencial"] or _hash(conta["email"].strip().lower()) != op["email_hash"]:
                raise ErroContrato("LINK_INDISPONIVEL", 400)
            if self._estados(op, agora)[1] == "pendente":
                raise ErroContrato("ENVIO_EM_PROCESSAMENTO", 409, max(1, math.ceil((op["envio_limite_em"] - agora).total_seconds())))
            snapshot = copy.deepcopy((self.contas, self.sessoes, self.operacoes, self.auditoria))
            try:
                # PBKDF2 é somente representação protegida para a fixture local;
                # em Xano será obrigatório o mecanismo nativo password.
                sal = secrets.token_bytes(16)
                conta["senha_hash"] = "pbkdf2_sha256$" + sal.hex() + "$" + hashlib.pbkdf2_hmac("sha256", nova_senha.encode(), sal, 100_000).hex()
                conta["versao_credencial"] = conta.get("versao_credencial", 1) + 1
                self._terminal(op, "consumido", agora)
                for outra in self.operacoes.values():
                    if outra["conta_id"] == op["conta_id"] and outra is not op:
                        self._terminal(outra, "invalidado", agora)
                for sessao in self.sessoes.values():
                    if sessao["conta_acesso_id"] == op["conta_id"]:
                        sessao["revogada_em"] = agora
                self.auditoria.append(dict(operacao_id=op["operacao_id"], conta_id=op["conta_id"],
                                          data=agora, resultado="consumido"))
                if self.antes_commit:
                    self.antes_commit()
            except Exception:
                self.contas, self.sessoes, self.operacoes, self.auditoria = snapshot
                raise ErroContrato("SERVICO_INDISPONIVEL", 503) from None

    def revogar_links(self, conta_id: int) -> None:
        """Simula revogação emergencial explícita, sem restaurar credenciais."""
        with self._lock:
            agora = self._agora()
            for op in self.operacoes.values():
                if op["conta_id"] == conta_id:
                    self._terminal(op, "invalidado", agora)
