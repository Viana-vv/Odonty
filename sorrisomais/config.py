"""Configuração pública do cliente REST, sem credenciais administrativas."""

import math
import os
from dataclasses import dataclass
from urllib.parse import urlsplit


class ConfiguracaoInvalida(ValueError):
    pass


@dataclass(frozen=True)
class Configuracao:
    api_base_url: str
    timeout: float = 10

    @classmethod
    def do_ambiente(cls):
        url = os.getenv("XANO_API_BASE_URL", "").strip().rstrip("/")
        try:
            parsed = urlsplit(url)
            timeout = float(os.getenv("XANO_HTTP_TIMEOUT_SECONDS", "10"))
            valid = (parsed.scheme == "https" and parsed.hostname and parsed.path
                     and not parsed.username and not parsed.password
                     and not parsed.query and not parsed.fragment
                     and not any(c.isspace() for c in url)
                     and math.isfinite(timeout) and timeout > 0)
            # Força a validação da porta antes de construir requisições.
            parsed.port
        except (ValueError, TypeError):
            valid = False
        if not valid:
            raise ConfiguracaoInvalida("O acesso ainda não está configurado. Contate o responsável pela clínica.")
        return cls(url, timeout)
