"""Estado por conexão Streamlit; toda revalidação consulta o Xano."""

from datetime import datetime, timezone

from .api import Credencial, ErroAcesso

CHAVE = "credencial"


def limpar(estado):
    estado.pop(CHAVE, None)
    estado.pop("pagina_equipe", None)
    for chave in list(estado):
        if chave.startswith("cad_"):
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


def identificar(estado, cliente):
    credencial = estado.get(CHAVE)
    if credencial is None:
        return None
    try:
        if not isinstance(credencial, Credencial) or credencial.expira_em <= datetime.now(timezone.utc):
            raise ErroAcesso("Sua sessão expirou. Entre novamente.", 401)
        conta = cliente.identificar(credencial.token)
        if conta.expira_em != credencial.expira_em:
            raise ErroAcesso()
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
