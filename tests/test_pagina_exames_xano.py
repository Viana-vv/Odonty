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
        if method == "PATCH":
            st.session_state.setdefault("patch_calls", []).append((method, route, kwargs))
            return {{"exame": {{"id": 2, "situacao": kwargs["payload"]["situacao"]}}}}
        {f'raise ErroAcesso("Falha segura.", {erro})' if erro else f'return {{"exames": {exames!r}}}'}
renderizar(ClienteFalso(), SimpleNamespace(perfis={perfis!r}))
'''
    return AppTest.from_string(script, default_timeout=20).run()


def test_paciente_ve_apenas_resultado_liberado():
    app = abrir([{"id": 1, "tipo": "Panorâmico", "situacao": "Resultado disponível", "resultado": "Resultado fictício"}])
    assert not app.exception
    assert any("Resultado fictício" in item.value for item in app.markdown)


def test_paciente_nao_ve_resultado_antes_da_liberacao():
    app = abrir([{"id": 2, "tipo": "Exame fictício", "situacao": "Solicitado", "resultado": "Resultado confidencial fictício"}])
    assert not app.exception
    assert not any("Resultado confidencial fictício" in item.value for item in app.markdown)
    assert any("Resultado ainda não liberado" in item.value for item in app.info)


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
    assert any(item.label == "Tentar novamente" for item in app.button)


def test_profissional_tem_controles_para_avancar_situacao():
    app = abrir([{"id": 2, "tipo": "Radiografia fictícia", "situacao": "Solicitado"}], perfis=("profissional",))
    assert not app.exception
    assert any("Atualizar situação" in item.label for item in app.expander)
    assert any("Realizado" in item.options for item in app.selectbox)
    assert len(app.get("file_uploader")) == 0


def test_profissional_envia_transicao_realizado_ao_xano():
    app = abrir([{"id": 2, "tipo": "Radiografia fictícia", "situacao": "Solicitado"}], perfis=("profissional",))
    app.selectbox[0].set_value("Realizado").run()
    next(botao for botao in app.button if botao.label == "Salvar atualização").click().run()
    chamadas = app.session_state["patch_calls"]
    assert chamadas[0][0:2] == ("PATCH", "/exames/2/situacao")
    assert chamadas[0][2]["payload"]["situacao"] == "Realizado"
    assert chamadas[0][2]["payload"]["realizado_em"].startswith("20")


def test_profissional_precisa_informar_resultado_antes_de_liberar():
    app = abrir([{"id": 2, "tipo": "Radiografia fictícia", "situacao": "Realizado"}], perfis=("profissional",))
    next(campo for campo in app.text_area if campo.label == "Resultado *").set_value("Resultado fictício")
    next(botao for botao in app.button if botao.label == "Salvar atualização").click().run()
    payload = app.session_state["patch_calls"][0][2]["payload"]
    assert payload["situacao"] == "Resultado disponível"
    assert payload["resultado"] == "Resultado fictício"


def test_tela_bloqueia_liberacao_com_resultado_vazio():
    app = abrir([{"id": 2, "tipo": "Radiografia fictícia", "situacao": "Realizado"}], perfis=("profissional",))
    next(botao for botao in app.button if botao.label == "Salvar atualização").click().run()
    assert "patch_calls" not in app.session_state
    assert any("Informe o resultado" in erro.value for erro in app.error)


def test_paciente_nao_recebe_controles_de_alteracao():
    app = abrir([{"id": 2, "tipo": "Radiografia fictícia", "situacao": "Solicitado"}], perfis=("paciente",))
    assert not app.exception
    assert not any("Atualizar situação" in item.label for item in app.expander)
    assert not any("Salvar atualização" == item.label for item in app.button)
