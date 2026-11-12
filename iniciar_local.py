"""Inicia a equipe em localhost com recuperação de sessão após recarga."""

import os
from pathlib import Path
import subprocess
import sys


if __name__ == "__main__":
    ambiente = dict(os.environ, SORRISOMAIS_SESSAO_LOCAL="1")
    raise SystemExit(subprocess.call(
        [sys.executable, "-m", "streamlit", "run", "app.py", "--server.address=localhost",
         "--server.port=8501", "--browser.serverAddress=localhost"],
        cwd=Path(__file__).resolve().parent, env=ambiente,
    ))
