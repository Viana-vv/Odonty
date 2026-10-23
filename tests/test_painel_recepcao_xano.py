"""Testes do painel conectado da Recepção, sem chamadas de rede."""

from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import Mock
from zoneinfo import ZoneInfo

import pytest
from streamlit.testing.v1 import AppTest

from sorrisomais import paginas_equipe, sessao
from sorrisomais.api import Credencial, ErroAcesso


def renderizar_inicio(cliente, conta, pode_cadastrar=True):
    from sorrisomais import paginas_equipe

    paginas_equipe.renderizar_inicio(cliente, conta, False, pode_cadastrar, True)


def conta_teste(perfil="recepcionista"):
    return SimpleNamespace(nome="Camila Fictícia", perfis=(perfil,))


def consultas_ficticias():
    agora = datetime.now(ZoneInfo("America/Sao_Paulo"))
    dados = [
        (6, 6, "Agendada"),
        (1, 1, "Confirmada"),
        (2, 2, "Concluída"),
        (3, 3, "Em atendimento"),
        (4, 4, "Cancelada"),
        (5, 5, "Falta"),
    ]
    return [
        {
            "id": identificador,
            "paciente_id": identificador + 100,
            "profissional_id": 201,
            "situacao": situacao,
            "inicio_em": (agora + timedelta(hours=horas)).isoformat(),
            "fim_em": (agora + timedelta(hours=horas, minutes=30)).isoformat(),
            "paciente_nome": f"Paciente Fictício {identificador}",
            "profissional_nome": "Dra. Exemplo Fictícia",
            "procedimentos": ["Procedimento Fictício Confidencial"],
        }
        for identificador, horas, situacao in dados
    ]


def abrir_painel(cliente, perfil="recepcionista", pode_cadastrar=True):
    conta = conta_teste(perfil)
    app = AppTest.from_function(renderizar_inicio, args=(cliente, conta, pode_cadastrar))
    app.session_state[sessao.CHAVE] = Credencial(
        "token-ficticio", datetime.now(timezone.utc) + timedelta(minutes=5)
    )
    return app.run()


@pytest.fixture
def cliente_painel():
    cliente = Mock()
    cliente.listar_consultas.return_value = consultas_ficticias()
    return cliente


def texto_ui(app):
    return "\n".join(
        item.value for grupo in (app.title, app.header, app.subheader, app.markdown, app.caption, app.text, app.info, app.error)
        for item in grupo
    )


def test_painel_mostra_metricas_e_cinco_consultas_ordenadas_sem_procedimentos(cliente_painel):
    app = abrir_painel(cliente_painel)

    assert not app.exception
    assert any(item.value == "Olá, Camila! 👋" for item in app.title)
    assert "Paciente Fictício 1" in texto_ui(app)
    assert "Paciente Fictício 5" in texto_ui(app)
    assert "Paciente Fictício 6" not in texto_ui(app)
    assert "Procedimento Fictício Confidencial" not in texto_ui(app)
    assert all("procedimentos" not in consulta for consulta in
               app.session_state[paginas_equipe.CACHE_PAINEL_RECEPCAO]["consultas"])
    assert any("Realizada" in item.value for item in app.caption)
    assert any(item.value == "6 consultas" for item in app.caption)
    assert any("inicio-nova-consulta" == botao.key for botao in app.button)
    assert any(botao.key == "inicio-abrir-agenda" and not botao.disabled for botao in app.button)
    cliente_painel.listar_consultas.assert_called_once()
    args, kwargs = cliente_painel.listar_consultas.call_args
    assert args == ("token-ficticio",)
    assert set(kwargs) == {"inicio", "fim"}


def test_cache_e_atualizacao_manual_reutilizam_apenas_sessao_atual(cliente_painel):
    app = abrir_painel(cliente_painel)
    assert cliente_painel.listar_consultas.call_count == 1

    app.run()
    assert cliente_painel.listar_consultas.call_count == 1

    app.button(key="inicio-painel-atualizar").click().run()
    assert cliente_painel.listar_consultas.call_count == 2

    app.session_state[sessao.CHAVE] = Credencial(
        "outro-token-ficticio", datetime.now(timezone.utc) + timedelta(minutes=5)
    )
    app.run()
    assert cliente_painel.listar_consultas.call_count == 3
    assert cliente_painel.listar_consultas.call_args.args == ("outro-token-ficticio",)


def test_atalhos_abrem_somente_as_areas_operacionais_disponiveis(cliente_painel):
    app = abrir_painel(cliente_painel)

    app.button(key="inicio-abrir-agenda").click().run()
    assert app.session_state["pagina_equipe"] == "agenda"
    app.button(key="inicio-cadastrar-paciente").click().run()
    assert app.session_state["pagina_equipe"] == "paciente"

    sem_cadastro = abrir_painel(cliente_painel, pode_cadastrar=False)
    assert not any(botao.key == "inicio-cadastrar-paciente" for botao in sem_cadastro.button)


def test_cache_expira_e_refaz_consulta(cliente_painel, monkeypatch):
    tempo = [100.0]
    monkeypatch.setattr(paginas_equipe, "monotonic", lambda: tempo[0])
    app = abrir_painel(cliente_painel)

    tempo[0] += paginas_equipe.PAINEL_RECEPCAO_CACHE_TTL_SEGUNDOS + 1
    app.run()

    assert cliente_painel.listar_consultas.call_count == 2


def test_dia_vazio_mostra_estado_vazio_e_indicadores_zero(cliente_painel):
    cliente_painel.listar_consultas.return_value = []
    app = abrir_painel(cliente_painel)

    assert any("Nenhuma consulta para hoje" in item.value for item in app.info)
    assert any("0 consultas" in item.value for item in app.caption)
    assert any("nenhuma marcada" in item.value for item in app.caption)
    assert any(botao.key == "inicio-abrir-agenda" and not botao.disabled for botao in app.button)


@pytest.mark.parametrize(
    ("status", "mensagem"),
    [
        (401, "Sua sessão expirou"),
        (403, "não tem permissão"),
        (503, "Não foi possível carregar o resumo"),
    ],
)
def test_falhas_removem_dados_e_nao_exibem_detalhes(cliente_painel, status, mensagem):
    cliente_painel.listar_consultas.side_effect = ErroAcesso("erro técnico privado", status)
    app = abrir_painel(cliente_painel)

    assert any(mensagem in item.value for item in app.error)
    assert "erro técnico privado" not in texto_ui(app)
    assert "Paciente Fictício" not in texto_ui(app)
    assert paginas_equipe.CACHE_PAINEL_RECEPCAO not in app.session_state
    if status == 401:
        assert sessao.CHAVE not in app.session_state


def test_atualizacao_com_falha_nao_reutiliza_resposta_antiga(cliente_painel):
    respostas = [consultas_ficticias(), ErroAcesso("falha técnica privada", 503)]
    cliente_painel.listar_consultas.side_effect = respostas
    app = abrir_painel(cliente_painel)
    assert "Paciente Fictício 1" in texto_ui(app)

    app.button(key="inicio-painel-atualizar").click().run()

    assert any("Não foi possível carregar o resumo" in item.value for item in app.error)
    assert "Paciente Fictício 1" not in texto_ui(app)
    assert paginas_equipe.CACHE_PAINEL_RECEPCAO not in app.session_state


def test_limite_de_requisicoes_aguarda_antes_de_tentar_novamente(cliente_painel, monkeypatch):
    tempo = [100.0]
    monkeypatch.setattr(paginas_equipe, "monotonic", lambda: tempo[0])
    cliente_painel.listar_consultas.side_effect = [
        ErroAcesso("limite técnico privado", 429), []
    ]
    app = abrir_painel(cliente_painel)

    assert any("Muitas tentativas" in item.value for item in app.error)
    tempo[0] += 10
    app.run()
    assert cliente_painel.listar_consultas.call_count == 1

    tempo[0] += paginas_equipe.PAINEL_RECEPCAO_RETRY_SEGUNDOS - 10
    app.button(key="inicio-painel-atualizar").click().run()
    assert cliente_painel.listar_consultas.call_count == 2
    assert any("Nenhuma consulta para hoje" in item.value for item in app.info)


def test_expiracao_e_logout_limpa_cache_do_painel(cliente_painel):
    app = abrir_painel(cliente_painel)
    assert paginas_equipe.CACHE_PAINEL_RECEPCAO in app.session_state

    estado = {
        sessao.CHAVE: app.session_state[sessao.CHAVE],
        paginas_equipe.CACHE_PAINEL_RECEPCAO: app.session_state[paginas_equipe.CACHE_PAINEL_RECEPCAO],
    }
    sessao.limpar(estado)

    assert paginas_equipe.CACHE_PAINEL_RECEPCAO not in estado


def test_credencial_expirada_nao_usa_cache_nem_consulta_api(cliente_painel):
    conta = conta_teste()
    app = AppTest.from_function(renderizar_inicio, args=(cliente_painel, conta, True))
    app.session_state[sessao.CHAVE] = Credencial(
        "token-expirado-ficticio", datetime.now(timezone.utc) - timedelta(seconds=1)
    )
    app.session_state[paginas_equipe.CACHE_PAINEL_RECEPCAO] = {
        "sessao": "identificador-ficticio",
        "dia": datetime.now(ZoneInfo("America/Sao_Paulo")).date(),
        "consultas": consultas_ficticias(),
        "carregado_em": 100.0,
    }

    app.run()

    assert any("Sua sessão expirou" in item.value for item in app.error)
    assert "Paciente Fictício" not in texto_ui(app)
    assert paginas_equipe.CACHE_PAINEL_RECEPCAO not in app.session_state
    cliente_painel.listar_consultas.assert_not_called()
