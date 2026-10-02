"""Estado por conexão Streamlit; identidade é atualizada com limite de chamadas."""

from datetime import datetime, timedelta, timezone

from .api import ContaAcesso, Credencial, ErroAcesso

CHAVE = "credencial"
CHAVE_CONTA = "conta_acesso_cache"
CHAVE_VERIFICADA = "conta_acesso_verificada_em"
INTERVALO_REVALIDACAO_SEGUNDOS = 20


def limpar(estado):
    for chave in (CHAVE, CHAVE_CONTA, CHAVE_VERIFICADA, "cad_especialidades_cache",
                  "cad_especialidades_cache_em", "cad_especialidades_erro_em"):
        estado.pop(chave, None)
    estado.pop("pagina_equipe", None)
    for chave in list(estado):
        if chave.startswith(("cad_", "pac_")):
            estado.pop(chave, None)


def entrar(estado, cliente, email, senha):
    limpar(estado)
    credencial = cliente.entrar(email, senha)
    try:
        conta = cliente.identificar(credencial.token)
        if conta.expira_em != credencial.expira_em:
            raise ErroAcesso()
    except ErroAcesso:
        try:
            cliente.sair(credencial.token)
        except ErroAcesso:
            pass
        raise
    estado[CHAVE] = credencial
    estado[CHAVE_CONTA] = conta
    estado[CHAVE_VERIFICADA] = datetime.now(timezone.utc)


def identificar(estado, cliente):
    credencial = estado.get(CHAVE)
    if credencial is None:
        return None
    try:
        if not isinstance(credencial, Credencial) or credencial.expira_em <= datetime.now(timezone.utc):
            raise ErroAcesso("Sua sessão expirou. Entre novamente.", 401)
        agora = datetime.now(timezone.utc)
        conta_cache = estado.get(CHAVE_CONTA)
        verificada_em = estado.get(CHAVE_VERIFICADA)
        if (isinstance(conta_cache, ContaAcesso)
                and conta_cache.expira_em == credencial.expira_em
                and isinstance(verificada_em, datetime)
                and timedelta(0) <= agora - verificada_em
                < timedelta(seconds=INTERVALO_REVALIDACAO_SEGUNDOS)):
            return conta_cache
        conta = cliente.identificar(credencial.token)
        if conta.expira_em != credencial.expira_em:
            raise ErroAcesso()
        estado[CHAVE_CONTA] = conta
        estado[CHAVE_VERIFICADA] = agora
        return conta
    except ErroAcesso:
        limpar(estado)
        raise


def sair(estado, cliente):
    credencial = estado.get(CHAVE)
    try:
        if credencial:
            cliente.sair(credencial.token)
        return "Você saiu com segurança."
    except ErroAcesso:
        return ("Você saiu deste acesso, mas não foi possível confirmar o encerramento no servidor. "
                "A sessão expira em até uma hora.")
    finally:
        limpar(estado)
