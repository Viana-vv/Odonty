"""Testes da página independente de Procedimentos de uma Consulta."""
from pathlib import Path
import pytest
from streamlit.testing.v1 import AppTest


def abrir(procedimentos, *, perfis=("profissional",), consulta=None, erro=None, erro_realizacao=None):
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
        st.session_state["chamadas_realizacao"] = st.session_state.get("chamadas_realizacao", 0) + 1
        {f'raise ErroAcesso("Falha segura na realização.", {erro_realizacao})' if erro_realizacao else 'pass'}
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

    app.button[0].click().run()

    assert not app.exception
    assert any("Procedimento marcado como realizado." in bloco.value for bloco in app.success)
    assert any("Realizado por Dra. Fictícia" in bloco.value for bloco in app.caption)
    assert not any(botao.label == "Marcar como realizado" for botao in app.button)
    assert not any(bloco.value == "Planejado" for bloco in app.info)
    assert any(bloco.value == "Realizado" for bloco in app.success)
    assert app.session_state["chamadas_realizacao"] == 1
    app.run()
    assert not app.exception
    assert not any(botao.label == "Marcar como realizado" for botao in app.button)
    assert app.session_state["chamadas_realizacao"] == 1


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


@pytest.mark.parametrize("status", [403, 404, 409, 429, 503])
def test_falha_na_realizacao_preserva_os_demais_itens_e_permite_tentar_novamente(status):
    segundo = {**item(), "id": 32, "procedimento_nome": "Restauração fictícia"}
    app = abrir([item(), segundo], erro_realizacao=status)
    app.button[0].click().run()

    assert not app.exception
    assert any("Falha segura na realização." in bloco.value for bloco in app.error)
    assert any(bloco.value == "Restauração fictícia" for bloco in app.subheader)
    assert len([botao for botao in app.button if botao.label == "Marcar como realizado"]) == 2
    assert not app.success
    assert app.session_state["chamadas_realizacao"] == 1


def test_sessao_expirada_na_realizacao_interrompe_as_acoes_protegidas():
    app = abrir([item()], erro_realizacao=401)
    app.button[0].click().run()

    assert not app.exception
    assert any("Sua sessão expirou" in bloco.value for bloco in app.error)
    assert "credencial" not in app.session_state
    assert not any(botao.label == "Marcar como realizado" for botao in app.button)
