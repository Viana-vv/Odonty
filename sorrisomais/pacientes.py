"""Validações do formulário; o Xano deve repetir as regras antes de gravar."""

import re
from datetime import date, datetime
from uuid import UUID
from zoneinfo import ZoneInfo

from .api import ErroAcesso


def hoje():
    return datetime.now(ZoneInfo("America/Sao_Paulo")).date()


def _texto(valor, campo, obrigatorio=False):
    if valor is None and not obrigatorio:
        return None
    if not isinstance(valor, str):
        raise ErroAcesso(f"Informe {campo} válido.", 400)
    valor = valor.strip()
    if not valor:
        if obrigatorio:
            raise ErroAcesso(f"Preencha {campo}.", 400)
        return None
    return valor


def validar_cadastro(nome, data_nascimento, telefone, cpf, email, celular):
    nome = _texto(nome, "o nome completo", True)
    if not 2 <= len(nome) <= 120:
        raise ErroAcesso("O nome deve ter de 2 a 120 caracteres.", 400)
    if not isinstance(data_nascimento, str) or not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", data_nascimento):
        raise ErroAcesso("Preencha uma data de nascimento válida (AAAA-MM-DD).", 400)
    try:
        nascimento = date.fromisoformat(data_nascimento)
    except ValueError:
        raise ErroAcesso("Informe uma data de nascimento válida.", 400) from None
    if nascimento > hoje():
        raise ErroAcesso("A data de nascimento não pode estar no futuro.", 400)
    cpf = _texto(cpf, "um CPF", True)
    if not re.fullmatch(r"(?:[0-9]{11}|[0-9]{3}\.[0-9]{3}\.[0-9]{3}-[0-9]{2})", cpf):
        raise ErroAcesso("Informe um CPF válido.", 400)
    cpf = cpf.replace(".", "").replace("-", "")
    digitos = [int(d) for d in cpf]
    valido = len(set(cpf)) > 1
    for tamanho in (9, 10):
        resto = sum(d * peso for d, peso in zip(digitos[:tamanho], range(tamanho + 1, 1, -1))) % 11
        valido = valido and digitos[tamanho] == (0 if resto < 2 else 11 - resto)
    if not valido:
        raise ErroAcesso("Informe um CPF válido.", 400)
    email = _texto(email, "um e-mail", True).lower()
    if len(email) > 254 or not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
        raise ErroAcesso("Informe um e-mail válido.", 400)
    telefone = _telefone(telefone, "um telefone")
    celular = _telefone(celular, "um celular")
    return dict(nome=nome, data_nascimento=data_nascimento, telefone=telefone,
                cpf=cpf, email=email, celular=celular)


def _telefone(valor, campo):
    valor = _texto(valor, campo, True)
    if not re.fullmatch(r"[0-9 ()-]+", valor):
        raise ErroAcesso(f"Informe {campo} nacional com 10 ou 11 dígitos.", 400)
    digitos = re.sub(r"[ ()-]", "", valor)
    if len(digitos) not in (10, 11):
        raise ErroAcesso(f"Informe {campo} nacional com 10 ou 11 dígitos.", 400)
    return digitos


def validar_operacao(operacao_id):
    try:
        operacao = UUID(operacao_id) if isinstance(operacao_id, str) else None
    except ValueError:
        operacao = None
    if operacao is None or operacao.version != 4 or str(operacao) != operacao_id:
        raise ErroAcesso("A operação de cadastro não é válida. Abra um novo cadastro.", 400)
    return operacao_id
