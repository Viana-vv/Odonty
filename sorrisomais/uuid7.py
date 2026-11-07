"""UUIDv7 RFC 9562 para Python 3.10+, sem pacote ou runtime adicional.

Identifica a operação idempotente; nunca é token de redefinição ou de sessão.
O servidor ainda precisa conferir o timestamp na primeira reserva.
"""

import re
import secrets
from datetime import datetime, timedelta, timezone
from uuid import RFC_4122, UUID

_FORMATO = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-7[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}\Z")
_EPOCA = datetime(1970, 1, 1, tzinfo=timezone.utc)


def validar_uuid7(valor):
    """Exige string canônica minúscula, versão 7 e variante RFC."""
    if not isinstance(valor, str) or not _FORMATO.fullmatch(valor):
        raise ValueError("Identificador de operação inválido.")
    identificador = UUID(valor)
    if identificador.variant != RFC_4122 or identificador.version != 7:
        raise ValueError("Identificador de operação inválido.")
    return identificador


def instante_uuid7(valor):
    return _EPOCA + timedelta(milliseconds=validar_uuid7(valor).int >> 80)


def gerar_uuid7(agora=None):
    """Timestamp UTC em ms e 74 bits aleatórios; sem promessa de monotonicidade."""
    agora = datetime.now(timezone.utc) if agora is None else agora
    if not isinstance(agora, datetime) or agora.utcoffset() is None:
        raise ValueError("Informe uma data com fuso horário.")
    intervalo = agora.astimezone(timezone.utc) - _EPOCA
    milissegundos = intervalo // timedelta(milliseconds=1)
    if not 0 <= milissegundos < 1 << 48:
        raise ValueError("Data fora do intervalo UUIDv7.")
    aleatorio = secrets.randbits(74)
    inteiro = ((milissegundos << 80) | (7 << 76)
               | ((aleatorio >> 62) << 64) | (2 << 62)
               | (aleatorio & ((1 << 62) - 1)))
    return str(UUID(int=inteiro))
