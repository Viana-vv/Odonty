"""Testes da página independente de Procedimentos de uma Consulta."""
from pathlib import Path
from streamlit.testing.v1 import AppTest


def abrir(procedimentos, *, perfis=("profissional",), consulta=None, erro=None):
    script = f'''\
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys
from types import SimpleNamespace
import streamlit as st
sys.path.insert(0, {str(Path(__file__).resolve().parents[1])!r})
from sorrisomais.api import Credencial, ErroAcesso
from sorrisomais import sessao
from sorrisomais.pagina_procedimentos_consulta import renderizar
st.session_state[sessao.CHAVE] = Credencial("token-ficticio", datetime.now(timezone.utc) + timedelta(hours=1))
if "itens_teste_procedimentos" not in st.session_state:
    st.session_state["itens_teste_procedimentos"] = {procedimentos!r}
class ClienteFalso:
    def listar_procedimentos_consulta(self, token, consulta_id):
        {f'raise ErroAcesso("Falha segura.", {erro})' if erro else 'return st.session_state["itens_teste_procedimentos"]'}
    def marcar_procedimento_realizado(self, token, consulta_id, vinculo_id):
        for item in st.session_state["itens_teste_procedimentos"]:
            if item["id"] == vinculo_id:
                item.update({{"situacao": "realizado", "realizado_por_nome": "Dra. Fictícia", "realizado_em": "2026-10-24T10:00:00Z"}})
                return item
        raise ErroAcesso("Não encontrado.", 404)
renderizar(ClienteFalso(), SimpleNamespace(perfis={perfis!r}), {consulta or {"id": 12, "paciente_nome": "Paciente Fictício"}!r})
'''
    return AppTest.from_string(script, default_timeout=20).run()


def item(situacao="planejado"):
    return {
        "id": 31,
        "procedimento_nome": "Profilaxia fictícia",
        "situacao": situacao,
        "profissional_planejamento_nome": "Dra. Planejadora",
        "criado_em": "2026-10-20T10:00:00Z",
        "realizado_por_nome": "Dra. Fictícia" if situacao == "realizado" else None,
        "realizado_em": "2026-10-24T10:00:00Z" if situacao == "realizado" else None,
    }


def test_tela_exibe_planejamento_e_permite_realizacao():
    app = abrir([item()])
    assert not app.exception
    assert any(botao.label == "Marcar como realizado" for botao in app.button)
    assert any("Planejado por Dra. Planejadora" in bloco.value for bloco in app.caption)

    app.button(key="marcar-procedimento-realizado-31").click().run()

    assert not app.exception
    assert any("Procedimento marcado como realizado." in bloco.value for bloco in app.success)
    assert any("Realizado por Dra. Fictícia" in bloco.value for bloco in app.caption)
    app.run()
    assert not app.exception
    assert not any(botao.label == "Marcar como realizado" for botao in app.button)


def test_tela_realizado_nao_expoe_acao_e_lista_vazia_tem_estado():
    realizado = abrir([item("realizado")])
    assert not realizado.exception
    assert not any(botao.label == "Marcar como realizado" for botao in realizado.button)
    assert any("Realizado por Dra. Fictícia" in bloco.value for bloco in realizado.caption)

    vazia = abrir([])
    assert not vazia.exception
    assert any("não possui Procedimentos" in bloco.value for bloco in vazia.info)


def test_tela_trata_permissao_e_falha_de_api_sem_simular_realizacao():
    administrativa = abrir([item()], perfis=("recepcionista",))
    assert not administrativa.exception
    assert any("somente para Profissionais" in bloco.value for bloco in administrativa.warning)
    assert not any(botao.label == "Marcar como realizado" for botao in administrativa.button)

    falha = abrir([item()], erro=503)
    assert not falha.exception
    assert any("Falha segura." in bloco.value for bloco in falha.error)
    assert not any(botao.label == "Marcar como realizado" for botao in falha.button)


def test_tela_expirada_limpa_sessao():
    app = abrir([item()], erro=401)
    assert not app.exception
    assert any("Sua sessão expirou" in bloco.value for bloco in app.error)
