"""Valida formatos públicos dos contratos de Agenda e Registro Clínico."""

from datetime import datetime


class DadosContratoInvalidos(ValueError):
    """Entrada incompatível com os contratos REST de Agenda/Registros Clínicos."""


SITUACOES_CONSULTA = {
    "Agendada", "Confirmada", "Em atendimento", "Realizada", "Cancelada", "Falta",
}


def validar_id(valor, campo="identificador"):
    if type(valor) is not int or valor <= 0:
        raise DadosContratoInvalidos(f"Informe um {campo} válido.")
    return valor


def validar_data_hora(valor, campo):
    if not isinstance(valor, str) or not valor.strip():
        raise DadosContratoInvalidos(f"Informe {campo} válido.")
    try:
        data_hora = datetime.fromisoformat(valor.strip().replace("Z", "+00:00"))
    except ValueError:
        raise DadosContratoInvalidos(f"Informe {campo} válido.") from None
    if data_hora.tzinfo is None or data_hora.utcoffset() is None:
        raise DadosContratoInvalidos(f"Informe {campo} com fuso horário.")
    return valor.strip()


def validar_intervalo(inicio, fim):
    inicio_texto = validar_data_hora(inicio, "o início")
    fim_texto = validar_data_hora(fim, "o fim")
    inicio_dt = datetime.fromisoformat(inicio_texto.replace("Z", "+00:00"))
    fim_dt = datetime.fromisoformat(fim_texto.replace("Z", "+00:00"))
    if fim_dt <= inicio_dt:
        raise DadosContratoInvalidos("O fim deve ser posterior ao início.")
    return inicio_texto, fim_texto


def validar_ids_procedimentos(valores):
    if not isinstance(valores, list):
        raise DadosContratoInvalidos("Informe a lista de Procedimentos.")
    if any(type(valor) is not int or valor <= 0 for valor in valores):
        raise DadosContratoInvalidos("A lista de Procedimentos contém identificador inválido.")
    if len(set(valores)) != len(valores):
        raise DadosContratoInvalidos("A lista de Procedimentos não pode conter duplicatas.")
    return list(valores)


def validar_texto(valor, campo, tamanho_maximo=8000):
    if not isinstance(valor, str) or not valor.strip() or len(valor.strip()) > tamanho_maximo:
        raise DadosContratoInvalidos(f"Informe {campo} válido.")
    return valor.strip()


def validar_transicao_consulta(atual, nova):
    transicoes = {
        "Agendada": {"Confirmada", "Cancelada", "Falta"},
        "Confirmada": {"Em atendimento", "Cancelada", "Falta"},
        "Em atendimento": {"Realizada"},
    }
    if nova not in SITUACOES_CONSULTA or nova not in transicoes.get(atual, set()):
        raise DadosContratoInvalidos("A transição da situação da Consulta não é permitida.")
    return nova
