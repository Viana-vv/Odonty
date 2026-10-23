"""Testes do painel conectado da Administração, sem chamadas de rede."""

from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import Mock
from zoneinfo import ZoneInfo

import pytest
from streamlit.testing.v1 import AppTest

from sorrisomais import paginas_equipe, sessao
from sorrisomais.api import Credencial, ErroAcesso


def renderizar_inicio(cliente, conta):
    from sorrisomais import paginas_equipe

    paginas_equipe.renderizar_inicio(cliente, conta, True, True, True)


def conta_teste(perfis=("administrador",)):
    return SimpleNamespace(nome="Ana Administradora Fictícia", perfis=perfis)


def consultas_ficticias():
    agora = datetime.now(ZoneInfo("America/Sao_Paulo"))
    situacoes = ((1, "Agendada"), (2, "Confirmada"), (3, "Concluída"),
                 (4, "Em atendimento"), (5, "Cancelada"), (6, "Falta"))
    return [
        {
            "id": identificador,
            "paciente_id": identificador + 100,
            "profissional_id": 201,
            "situacao": situacao,
            "inicio_em": (agora + timedelta(minutes=identificador * 15)).isoformat(),
            "fim_em": (agora + timedelta(minutes=identificador * 15 + 30)).isoformat(),
            "paciente_nome": f"Paciente Fictício {identificador}",
            "profissional_nome": "Dra. Exemplo Fictícia",
            "procedimentos": ["Procedimento Fictício Confidencial"],
        }
        for identificador, situacao in situacoes
    ]


def abrir_painel(cliente):
    app = AppTest.from_function(renderizar_inicio, args=(cliente, conta_teste()))
    app.session_state[sessao.CHAVE] = Credencial(
        "token-ficticio", datetime.now(timezone.utc) + timedelta(minutes=5)
    )
    return app.run()


@pytest.fixture
def cliente_painel():
    cliente = Mock()
    cliente.listar_consultas.return_value = consultas_ficticias()
    cliente.listar_opcoes_agenda.return_value = {
        "pacientes": [{"id": 1, "nome": "Paciente Fictício A"},
                      {"id": 2, "nome": "Paciente Fictício B"}],
        "profissionais": [],
        "procedimentos": [],
    }
    return cliente


def texto_ui(app):
    return "\n".join(
        item.value for grupo in (app.title, app.header, app.subheader, app.markdown,
                                 app.caption, app.text, app.info, app.error)
        for item in grupo
    )


def test_painel_calcula_metricas_e_mostra_ate_cinco_consultas(cliente_painel):
    app = abrir_painel(cliente_painel)

    assert not app.exception
    assert any(item.value == "Olá, Ana! 👋" for item in app.title)
    assert any(item.value == "Consultas hoje" for item in app.caption)
    assert any(item.value == "Pacientes ativos" for item in app.caption)
    assert any(">6</strong>" in item.value for item in app.markdown)
    assert any(">1</strong>" in item.value for item in app.markdown)
    assert any(">2</strong>" in item.value for item in app.markdown)
    horario_proxima = datetime.fromisoformat(
        cliente_painel.listar_consultas.return_value[0]["inicio_em"]
    ).strftime("%H:%M")
    assert any(f">{horario_proxima}</strong>" in item.value for item in app.markdown)
    assert "Paciente Fictício 1" in texto_ui(app)
    assert "Paciente Fictício 5" in texto_ui(app)
    assert "Paciente Fictício 6" not in texto_ui(app)
    assert "Paciente Fictício A" not in texto_ui(app)
    assert "Procedimento Fictício Confidencial" not in texto_ui(app)
    assert "Realizada" in texto_ui(app)
    cliente_painel.listar_consultas.assert_called_once()
    cliente_painel.listar_opcoes_agenda.assert_called_once_with("token-ficticio")
    args, kwargs = cliente_painel.listar_consultas.call_args
    assert args == ("token-ficticio",)
    assert set(kwargs) == {"inicio", "fim"}


def test_estado_vazio_mantem_atalhos_disponiveis(cliente_painel):
    cliente_painel.listar_consultas.return_value = []
    app = abrir_painel(cliente_painel)

    assert not app.exception
    assert any("Nenhuma consulta para hoje" in item.value for item in app.info)
    assert any(botao.key == "inicio-abrir-agenda" and not botao.disabled for botao in app.button)
    assert any(botao.key == "inicio-cadastrar-paciente" for botao in app.button)


@pytest.mark.parametrize(
    ("metodo", "status", "mensagem"),
    [
        ("listar_consultas", 401, "Sua sessão expirou"),
        ("listar_opcoes_agenda", 403, "não tem permissão"),
        ("listar_consultas", 503, "Não foi possível carregar o resumo"),
    ],
)
def test_falhas_descartam_resumo_e_mostram_mensagem_segura(
        cliente_painel, metodo, status, mensagem):
    getattr(cliente_painel, metodo).side_effect = ErroAcesso("erro técnico privado", status)
    app = abrir_painel(cliente_painel)

    assert any(mensagem in item.value for item in app.error)
    assert "erro técnico privado" not in texto_ui(app)
    assert "Paciente Fictício" not in texto_ui(app)
    if status == 401:
        assert sessao.CHAVE not in app.session_state


def test_falha_na_segunda_leitura_nao_exibe_consultas_parciais(cliente_painel):
    cliente_painel.listar_opcoes_agenda.side_effect = ErroAcesso("falha privada", 503)
    app = abrir_painel(cliente_painel)

    assert any("Não foi possível carregar o resumo" in item.value for item in app.error)
    assert "Paciente Fictício 1" not in texto_ui(app)
    assert "Paciente Fictício A" not in texto_ui(app)


def test_perfis_sem_administrador_nao_carregam_dados_administrativos(cliente_painel):
    conta = conta_teste(("profissional",))
    app = AppTest.from_function(renderizar_inicio, args=(cliente_painel, conta))
    app.session_state[sessao.CHAVE] = Credencial(
        "token-ficticio", datetime.now(timezone.utc) + timedelta(minutes=5)
    )

    app.run()

    cliente_painel.listar_opcoes_agenda.assert_not_called()
