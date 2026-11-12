"""Recuperação em localhost; credenciais permanecem apenas na memória."""

import math
import secrets
import threading
import time
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit

COOKIE = "sorrisomais_sessao_local"
CHAVE = "sessao_local_id"
DESTINO = "http://localhost:8501/"


class SessoesLocais:
    def __init__(self):
        self.sessoes = {}
        self.tickets = {}
        self.lock = threading.Lock()

    def _limpar(self):
        agora = time.time()
        self.sessoes = {k: v for k, v in self.sessoes.items() if v[1] > agora}
        self.tickets = {k: v for k, v in self.tickets.items()
                        if v[1] > agora and v[0] in self.sessoes}

    def criar(self, credencial):
        with self.lock:
            self._limpar()
            prazo = min(credencial.expira_em.timestamp(), time.time() + 28800)
            if prazo <= time.time():
                raise ValueError("Sessão expirada.")
            identificador = secrets.token_urlsafe(32)
            ticket = secrets.token_urlsafe(32)
            self.sessoes[identificador] = (credencial, prazo)
            self.tickets[ticket] = (identificador, time.time() + 60)
            return identificador, ticket

    def consumir(self, ticket):
        with self.lock:
            self._limpar()
            valor = self.tickets.pop(ticket, None)
            if valor is None:
                return None
            identificador = valor[0]
            return identificador, max(1, math.floor(self.sessoes[identificador][1] - time.time()))

    def recuperar(self, identificador):
        with self.lock:
            self._limpar()
            valor = self.sessoes.get(identificador)
            return valor[0] if valor else None

    def revogar(self, identificador):
        with self.lock:
            self.sessoes.pop(identificador, None)
            self._limpar()


def criar_servidor(armazenamento, porta=8502):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass  # URLs de ativação contêm capacidades temporárias.

        def do_GET(self):
            url = urlsplit(self.path)
            if (self.headers.get("Host") != f"localhost:{self.server.server_port}"
                    or self.headers.get("Sec-Fetch-Site") == "cross-site"
                    or url.path != "/ativar"):
                self.send_error(404)
                return
            ticket = parse_qs(url.query).get("ticket", [""])[0]
            resultado = armazenamento.consumir(ticket)
            if resultado is None:
                self.send_response(410)
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write("Ativação expirada. Volte ao aplicativo e tente novamente.".encode())
                return
            identificador, duracao = resultado
            cookie = SimpleCookie()
            cookie[COOKIE] = identificador
            cookie[COOKIE]["httponly"] = True
            cookie[COOKIE]["samesite"] = "Strict"
            cookie[COOKIE]["path"] = "/"
            cookie[COOKIE]["max-age"] = duracao
            self.send_response(303)
            self.send_header("Set-Cookie", cookie.output(header="").strip())
            self.send_header("Location", DESTINO)
            self.send_header("Cache-Control", "no-store")
            self.send_header("Referrer-Policy", "no-referrer")
            self.end_headers()

    return ThreadingHTTPServer(("127.0.0.1", porta), Handler)


def servico():
    return _servico_cacheado()


import streamlit as st


@st.cache_resource(show_spinner=False)
def _servico_cacheado():
    armazenamento = SessoesLocais()
    servidor = criar_servidor(armazenamento)
    threading.Thread(target=servidor.serve_forever, daemon=True).start()
    return armazenamento


def habilitado():
    import os

    return os.getenv("SORRISOMAIS_SESSAO_LOCAL") == "1"


def restaurar(estado, cookies):
    from . import sessao

    if not habilitado() or estado.get(sessao.CHAVE):
        return
    identificador = cookies.get(COOKIE)
    if not identificador:
        return
    credencial = servico().recuperar(identificador)
    if credencial:
        estado[sessao.CHAVE] = credencial
        estado[CHAVE] = identificador


def revogar(estado):
    identificador = estado.pop(CHAVE, None)
    pendente = estado.pop("sessao_local_pendente", None)
    if habilitado() and (identificador or pendente):
        for valor in (identificador, pendente):
            if valor:
                servico().revogar(valor)


def manter(estado):
    from . import sessao

    if (not habilitado() or estado.get(CHAVE)
            or estado.get("sessao_local_pendente") or not estado.get(sessao.CHAVE)):
        return
    identificador, ticket = servico().criar(estado[sessao.CHAVE])
    estado["sessao_local_pendente"] = identificador
    # Navegação no documento principal; o servidor emite o cookie HttpOnly
    # e retorna ao app. A nova conexão já recebe o cookie em st.context.
    st.html(
        '<script>window.location.replace('
        f'"http://localhost:8502/ativar?ticket={ticket}"'
        ');</script>', unsafe_allow_javascript=True,
    )
