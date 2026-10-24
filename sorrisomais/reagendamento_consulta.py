"""Contrato isolado de reagendamento; usa o transporte REST comum."""

from .api import ErroAcesso
from .contratos_clinicos import validar_id, validar_texto


def reagendar_consulta(cliente, token, consulta_id, disponibilidade_id, justificativa):
    """Envia uma operação atômica; nunca cancela e agenda em chamadas separadas."""
    cliente._token_obrigatorio(token)
    consulta_id = validar_id(consulta_id, "Consulta")
    disponibilidade_id = validar_id(disponibilidade_id, "Disponibilidade")
    payload = {
        "disponibilidade_id": disponibilidade_id,
        "justificativa": validar_texto(justificativa, "a justificativa", 1000),
    }
    data = cliente._request(
        "POST", f"/consultas/{consulta_id}/reagendamento", token=token,
        payload=payload, status_esperado=201,
    )
    campos = {"paciente_id": int, "profissional_id": int,
              "disponibilidade_id": int, "situacao": str}
    original = cliente._item_resposta(data, "consulta_original", campos)
    nova = cliente._item_resposta(data, "consulta", campos)
    if (original["id"] != consulta_id or original["situacao"] != "Cancelada"
            or nova["id"] == original["id"] or nova["situacao"] != "Agendada"
            or nova["paciente_id"] != original["paciente_id"]
            or nova["disponibilidade_id"] != disponibilidade_id
            or original["disponibilidade_id"] == disponibilidade_id
            or type(data.get("reagendamento_id")) is not int
            or data["reagendamento_id"] <= 0):
        raise ErroAcesso()
    return data
