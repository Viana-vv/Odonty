from datetime import datetime, timedelta, timezone
import ast
from pathlib import Path
from uuid import UUID, uuid4

import pytest

from sorrisomais.uuid7 import gerar_uuid7, instante_uuid7, validar_uuid7


def test_vetor_publicado_rfc_9562():
    valor = "017f22e2-79b0-7cc3-98c4-dc0c0c07398f"
    assert validar_uuid7(valor).version == 7
    assert instante_uuid7(valor) == datetime.fromtimestamp(1645557742, timezone.utc)


def test_bits_timestamp_variante_e_aleatoriedade():
    agora = datetime(2026, 11, 7, 18, 22, 33, 123999, tzinfo=timezone.utc)
    valores = {gerar_uuid7(agora) for _ in range(100)}
    assert len(valores) == 100
    assert all(validar_uuid7(v).version == 7 for v in valores)
    assert all(instante_uuid7(v) == agora.replace(microsecond=123000) for v in valores)


@pytest.mark.parametrize("valor", [None, 7, str(uuid4()),
    "017F22E2-79B0-7CC3-98C4-DC0C0C07398F", "017f22e279b07cc398c4dc0c0c07398f",
    "017f22e2-79b0-7cc3-78c4-dc0c0c07398f", "017f22e2-79b0-7cc3-98c4-dc0c0c07398f\n"])
def test_rejeita_identificadores_nao_canonicos(valor):
    with pytest.raises(ValueError):
        validar_uuid7(valor)


def test_aceita_fuso_e_rejeita_data_sem_fuso_ou_anterior_epoca():
    local = datetime(2026, 11, 7, tzinfo=timezone(timedelta(hours=-3)))
    assert instante_uuid7(gerar_uuid7(local)) == local.astimezone(timezone.utc)
    for data in (datetime(2026, 11, 7), datetime(1969, 1, 1, tzinfo=timezone.utc)):
        with pytest.raises(ValueError):
            gerar_uuid7(data)


def test_sintaxe_compativel_com_python_310_sem_uuid7_nativo():
    fonte = Path("sorrisomais/uuid7.py").read_text(encoding="utf-8")
    ast.parse(fonte, feature_version=(3, 10))
    assert UUID(gerar_uuid7()).version == 7
