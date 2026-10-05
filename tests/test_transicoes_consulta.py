import pytest

from sorrisomais.contratos_clinicos import DadosContratoInvalidos, validar_transicao_consulta


@pytest.mark.parametrize(("atual", "nova"), [
    ("Agendada", "Confirmada"),
    ("Agendada", "Cancelada"),
    ("Confirmada", "Em atendimento"),
    ("Confirmada", "Cancelada"),
    ("Confirmada", "Falta"),
    ("Em atendimento", "Realizada"),
])
def test_transicoes_permitidas(atual, nova):
    assert validar_transicao_consulta(atual, nova) == nova


@pytest.mark.parametrize(("atual", "nova"), [
    ("Agendada", "Falta"),
    ("Agendada", "Realizada"),
    ("Confirmada", "Realizada"),
    ("Realizada", "Agendada"),
    ("Cancelada", "Confirmada"),
    ("Falta", "Realizada"),
])
def test_transicoes_invalidas_sao_rejeitadas(atual, nova):
    with pytest.raises(DadosContratoInvalidos):
        validar_transicao_consulta(atual, nova)
