"""Estado e validações do fluxo de recuperação de senha."""

import re

from .api import ErroAcesso


def validar_email(email):
    email = email.strip().lower() if isinstance(email, str) else ""
    if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
        raise ErroAcesso("Informe um e-mail válido.", 400)
    return email


def validar_otp(otp):
    otp = otp.strip() if isinstance(otp, str) else ""
    if not re.fullmatch(r"[0-9]{6}", otp):
        raise ErroAcesso("Informe o código de seis dígitos recebido por e-mail.", 400)
    return otp


def validar_senhas(nova, confirmacao):
    if not isinstance(nova, str) or not 12 <= len(nova) <= 128:
        raise ErroAcesso("A nova senha deve ter entre 12 e 128 caracteres.", 400)
    if nova != confirmacao:
        raise ErroAcesso("As senhas não conferem.", 400)
    return nova

