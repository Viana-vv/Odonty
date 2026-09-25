"""Validação do formulário; a autorização e as regras definitivas pertencem ao Xano."""
import re

from .api import ErroAcesso, validar_campos

UFS = "AC AL AP AM BA CE DF ES GO MA MT MS MG PA PB PR PE PI RJ RN RS RO RR SC SP SE TO".split()


def validar_cadastro(nome, email, senha, cro, especialidade_id):
    if any(not isinstance(v, str) for v in (nome, email, senha, cro)):
        raise ErroAcesso("Confira os dados do profissional.", 400)
    nome = nome.strip()
    if not 2 <= len(nome) <= 120:
        raise ErroAcesso("Informe um nome com 2 a 120 caracteres.", 400)
    email = validar_campos(email, senha)
    if len(email) > 254:
        raise ErroAcesso("Informe um e-mail de até 254 caracteres.", 400)
    if not 12 <= len(senha) <= 128:
        raise ErroAcesso("A senha inicial deve ter entre 12 e 128 caracteres.", 400)
    cro = cro.strip().upper()
    partes = re.fullmatch(r"([A-Z]{2})-([0-9]{1,10})", cro)
    if (not partes or partes[1] not in UFS or int(partes[2]) <= 0 or len(cro) > 32):
        raise ErroAcesso("Informe o CRO no formato UF-NÚMERO, por exemplo SP-123456.", 400)
    if type(especialidade_id) is not int or especialidade_id <= 0:
        raise ErroAcesso("Selecione uma especialidade.", 400)
    return {"nome": nome, "email": email, "senha": senha,
            "cro": f"{partes[1]}-{int(partes[2])}", "especialidade_id": especialidade_id}
