from datetime import datetime, timedelta, timezone
from pathlib import Path

from streamlit.testing.v1 import AppTest


def abrir(exames, perfis=("paciente",), erro=None):
    script = f'''\
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys
from types import SimpleNamespace
import streamlit as st
sys.path.insert(0, {str(Path(__file__).resolve().parents[1])!r})
from sorrisomais.api import Credencial, ErroAcesso
from sorrisomais import sessao
from sorrisomais.pagina_exames_xano import renderizar
st.session_state[sessao.CHAVE] = Credencial("token-ficticio", datetime.now(timezone.utc) + timedelta(hours=1))
class ClienteFalso:
    def _request(self, method, route, **kwargs):
        {f'raise ErroAcesso("Falha segura.", {erro})' if erro else f'return {{"exames": {exames!r}}}'}
renderizar(ClienteFalso(), SimpleNamespace(perfis={perfis!r}))
'''
    return AppTest.from_string(script, default_timeout=20).run()


def test_paciente_ve_apenas_resultado_liberado():
    app = abrir([{"id": 1, "tipo": "Panorâmico", "situacao": "Resultado disponível", "resultado": "Resultado fictício"}])
    assert not app.exception
    assert any("Resultado fictício" in item.value for item in app.markdown)


def test_perfil_administrativo_nao_acessa_exames():
    app = abrir([], perfis=("recepcionista",))
    assert not app.exception
    assert any("não está disponível" in item.value for item in app.warning)


def test_estado_vazio():
    app = abrir([])
    assert not app.exception
    assert any("Nenhum Exame" in item.value for item in app.info)


def test_erro_api_nao_expoe_detalhes():
    app = abrir([], erro=503)
    assert not app.exception
    assert any("Não foi possível carregar os Exames" in item.value for item in app.error)
