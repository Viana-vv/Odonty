"""Contrato específico de leitura administrativa de Contas de Acesso."""

from .api import ErroAcesso

_CAMPOS_CONTA = ("id", "nome", "email", "perfis", "situacao")
_SITUACOES = {"ativo", "inativo", "bloqueado"}
_PERFIS = {"paciente", "profissional", "administrador", "recepcionista"}


def listar_contas_acesso(cliente, token):
    """Busca e valida a resposta mínima de GET /contas-acesso."""
    resposta = cliente._request("GET", "/contas-acesso", token=token)
    contas = resposta.get("contas_acesso") if isinstance(resposta, dict) else None
    if not isinstance(contas, list):
        raise ErroAcesso()

    resultado = []
    for conta in contas:
        if not isinstance(conta, dict):
            raise ErroAcesso()
        item = {campo: conta.get(campo) for campo in _CAMPOS_CONTA}
        if (type(item["id"]) is not int or not isinstance(item["nome"], str)
                or not isinstance(item["email"], str)
                or not isinstance(item["perfis"], list)
                or not item["perfis"]
                or any(not isinstance(perfil, str) or perfil not in _PERFIS
                       for perfil in item["perfis"])
                or not isinstance(item["situacao"], str)
                or item["situacao"] not in _SITUACOES):
            raise ErroAcesso()
        resultado.append(item)
    return resultado
