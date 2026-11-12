from datetime import datetime, timedelta, timezone
from unittest.mock import Mock
from io import BytesIO

import pytest

from sorrisomais.api import ContaAcesso, Credencial, ErroAcesso
from sorrisomais import sessao, sessao_local


def credencial():
    return Credencial("token-ficticio", datetime.now(timezone.utc) + timedelta(hours=1))


def test_ticket_unico_e_identificadores_isolados():
    memoria = sessao_local.SessoesLocais()
    primeira = credencial()
    identificador, ticket = memoria.criar(primeira)
    outro, _ = memoria.criar(credencial())
    assert outro != identificador
    assert memoria.recuperar(ticket) is None
    assert memoria.consumir(ticket)[0] == identificador
    assert memoria.consumir(ticket) is None
    assert memoria.recuperar(identificador) is primeira
    memoria.revogar(identificador)
    assert memoria.recuperar(identificador) is None
    assert memoria.recuperar(outro) is not None


def test_rota_ativacao_emite_cookie_http_only_e_recusa_ticket_repetido():
    memoria = sessao_local.SessoesLocais()
    _, ticket = memoria.criar(credencial())
    # Constrói o handler sem abrir socket ou enviar requisições à rede.
    servidor = Mock(server_port=8502)
    servidor.RequestHandlerClass = None
    from unittest.mock import patch
    with patch.object(sessao_local, "ThreadingHTTPServer", return_value=servidor) as fabrica:
        sessao_local.criar_servidor(memoria)
    handler = fabrica.call_args.args[1]

    def requisitar():
        entrada = BytesIO((f"GET /ativar?ticket={ticket} HTTP/1.0\r\nHost: localhost:8502\r\n\r\n").encode())
        saida = BytesIO()
        conexao = Mock()
        conexao.makefile.return_value = entrada
        conexao.sendall.side_effect = saida.write
        handler(conexao, ("127.0.0.1", 1234), servidor)
        return saida.getvalue().decode()

    resposta = requisitar()
    assert "303" in resposta
    assert "HttpOnly" in resposta
    assert "SameSite=Strict" in resposta
    assert "Location: http://localhost:8501/" in resposta
    assert "token-ficticio" not in resposta
    assert "410" in requisitar()


def test_ticket_e_sessao_expiram_sem_renovacao(monkeypatch):
    memoria = sessao_local.SessoesLocais()
    agora = sessao_local.time.time()
    identificador, ticket = memoria.criar(credencial())
    monkeypatch.setattr(sessao_local.time, "time", lambda: agora + 61)
    assert memoria.consumir(ticket) is None
    assert memoria.recuperar(identificador) is not None
    monkeypatch.setattr(sessao_local.time, "time", lambda: agora + 3601)
    assert memoria.recuperar(identificador) is None


def test_recuperacao_revalida_xano_e_logout_remove_cookie_logico(monkeypatch):
    monkeypatch.setenv("SORRISOMAIS_SESSAO_LOCAL", "1")
    memoria = sessao_local.SessoesLocais()
    monkeypatch.setattr(sessao_local, "servico", lambda: memoria)
    acesso = credencial()
    identificador, _ = memoria.criar(acesso)
    estado = {}
    sessao_local.restaurar(estado, {sessao_local.COOKIE: identificador})
    cliente = Mock()
    cliente.identificar.return_value = ContaAcesso(1, "Fictício", ("profissional",), acesso.expira_em)
    assert sessao.identificar(estado, cliente).id == 1
    cliente.identificar.assert_called_once_with(acesso.token)
    sessao.sair(estado, cliente)
    assert memoria.recuperar(identificador) is None
    assert not estado


def test_sessao_recusada_revoga_recuperacao(monkeypatch):
    monkeypatch.setenv("SORRISOMAIS_SESSAO_LOCAL", "1")
    memoria = sessao_local.SessoesLocais()
    monkeypatch.setattr(sessao_local, "servico", lambda: memoria)
    identificador, _ = memoria.criar(credencial())
    estado = {}
    sessao_local.restaurar(estado, {sessao_local.COOKIE: identificador})
    cliente = Mock()
    cliente.identificar.side_effect = ErroAcesso(status=401)
    with pytest.raises(ErroAcesso):
        sessao.identificar(estado, cliente)
    assert memoria.recuperar(identificador) is None
