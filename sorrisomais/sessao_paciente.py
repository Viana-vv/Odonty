"""Sessão de autoatendimento independente da sessão da equipe."""

from datetime import datetime, timezone

from .api import Credencial, ErroAcesso

CHAVE_CREDENCIAL = "paciente_credencial"
CHAVE_CONTA = "paciente_conta"


def limpar(estado):
    from .cache_xano import invalidar_cache
    invalidar_cache(estado)
    estado.pop(CHAVE_CREDENCIAL, None)
    estado.pop(CHAVE_CONTA, None)
    estado.pop("paciente_email", None)
    estado.pop("paciente_senha", None)
    estado.pop("paciente_entrada_pendente", None)


def entrar(estado, cliente, email, senha):
    limpar(estado)
    credencial = cliente.entrar(email, senha)
    try:
        conta = cliente.identificar(credencial.token)
        if conta.expira_em != credencial.expira_em:
            raise ErroAcesso()
        if "paciente" not in conta.perfis:
            raise ErroAcesso("Esta área é exclusiva para Pacientes.", 403)
    except ErroAcesso:
        try:
            cliente.sair(credencial.token)
        except ErroAcesso:
            pass
        raise
    estado[CHAVE_CREDENCIAL] = credencial
    estado[CHAVE_CONTA] = conta


def identificar(estado, cliente):
    credencial = estado.get(CHAVE_CREDENCIAL)
    if credencial is None:
        return None
    try:
        if not isinstance(credencial, Credencial) or credencial.expira_em <= datetime.now(timezone.utc):
            raise ErroAcesso("Sua sessão expirou. Entre novamente.", 401)
        conta = cliente.identificar(credencial.token)
        if conta.expira_em != credencial.expira_em:
            raise ErroAcesso()
        if "paciente" not in conta.perfis:
            raise ErroAcesso("Esta área é exclusiva para Pacientes.", 403)
        estado[CHAVE_CONTA] = conta
        return conta
    except ErroAcesso:
        limpar(estado)
        raise


def sair(estado, cliente):
    credencial = estado.get(CHAVE_CREDENCIAL)
    try:
        if credencial:
            cliente.sair(credencial.token)
        return "Você saiu com segurança."
    except ErroAcesso:
        return "Você saiu deste acesso, mas não foi possível confirmar o encerramento no servidor."
    finally:
        limpar(estado)
