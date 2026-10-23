"""Testes do painel do Profissional sem chamadas reais de rede."""

from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import Mock
from zoneinfo import ZoneInfo

import pytest
from streamlit.testing.v1 import AppTest

from sorrisomais import painel_profissional, sessao
from sorrisomais.api import Credencial, ErroAcesso

FUSO = ZoneInfo("America/Sao_Paulo")


def renderizar(cliente, conta):
    from sorrisomais import painel_profissional

    painel_profissional.renderizar(cliente, conta)


def conta_teste():
    return SimpleNamespace(nome="Dra. Conta Fictícia", perfis=("profissional",))


def abrir(cliente):
    app = AppTest.from_function(renderizar, args=(cliente, conta_teste()))
    app.session_state[sessao.CHAVE] = Credencial(
        "token-profissional-ficticio", datetime.now(timezone.utc) + timedelta(minutes=5)
    )
    return app.run()


def consultas_para_hoje():
    agora = datetime.now(FUSO).replace(second=0, microsecond=0)
    situacoes = (
        (-2, "Realizada"), (1, "Agendada"), (2, "Confirmada"),
        (3, "Cancelada"), (4, "Falta"), (5, "Concluída"), (6, "Agendada"),
    )
    return [
        {
            "id": indice,
            "inicio_em": (agora + timedelta(hours=horas)).isoformat(),
            "situacao": situacao,
            "paciente_nome": f"Paciente Fictício {indice}",
            "profissional_nome": "Dra. Profissional Fictícia",
            "procedimentos": ["Procedimento Fictício Confidencial"],
            "motivo": "Motivo administrativo privado",
        }
        for indice, (horas, situacao) in enumerate(situacoes, start=1)
    ]


def texto_ui(app):
    grupos = (app.title, app.header, app.subheader, app.markdown, app.caption,
              app.text, app.info, app.error)
    return "\n".join(item.value for grupo in grupos for item in grupo)


@pytest.fixture
def cliente_painel():
    cliente = Mock()
    cliente.listar_consultas.return_value = consultas_para_hoje()
    return cliente


def test_resumo_ordena_limita_e_omite_campos_clinicos(cliente_painel):
    app = abrir(cliente_painel)
    texto = texto_ui(app)

    assert not app.exception
    assert any(item.value == "Olá, Dra.! 👋" for item in app.title)
    assert all(rotulo in texto for rotulo in (
        "Consultas hoje", "Atendimentos", "Confirmadas", "Próxima consulta"
    ))
    assert "Paciente Fictício 2" in texto
    assert "Paciente Fictício 5" in texto
    assert "Paciente Fictício 6" not in texto
    assert "Paciente Fictício 7" not in texto
    assert "Procedimento Fictício Confidencial" not in texto
    assert "Motivo administrativo privado" not in texto
    assert "Dra. Profissional FictÃ­cia" not in texto
    assert any("<strong class='valor-metrica'>7</strong>" in item.value
               for item in app.markdown)
    assert sum(item.value == "Realizada" for item in app.caption) >= 1
    cliente_painel.listar_consultas.assert_called_once()
    args, parametros = cliente_painel.listar_consultas.call_args
    assert args == ("token-profissional-ficticio",)
    assert set(parametros) == {"inicio", "fim"}
    assert "profissional_id" not in parametros


def test_resumo_reutiliza_cache_diario_da_agenda(cliente_painel):
    app = abrir(cliente_painel)
    app.run()

    assert cliente_painel.listar_consultas.call_count == 1

    app.session_state[sessao.CHAVE] = Credencial(
        "outro-token-profissional-ficticio",
        datetime.now(timezone.utc) + timedelta(minutes=5),
    )
    app.run()
    assert cliente_painel.listar_consultas.call_count == 2
    assert cliente_painel.listar_consultas.call_args.args == ("outro-token-profissional-ficticio",)


def test_dia_vazio_mostra_estado_e_metricas_zero(cliente_painel):
    cliente_painel.listar_consultas.return_value = []
    app = abrir(cliente_painel)

    assert not app.exception
    assert any("Nenhuma consulta para hoje" in item.value for item in app.info)
    assert any("nenhuma marcada" in item.value for item in app.caption)
    assert any(item.value == "Agenda de hoje" for item in app.subheader)
    assert any(button.key == "painel-profissional-agenda-atalho" for button in app.button)


def test_resposta_invalida_mostra_erro_sem_linhas_parciais(cliente_painel):
    cliente_painel.listar_consultas.return_value = [
        {"inicio_em": "2026-10-23T10:00:00-03:00", "situacao": "Agendada"}
    ]
    app = abrir(cliente_painel)
    texto = texto_ui(app)

    assert any("Não foi possível carregar sua agenda" in item.value for item in app.error)
    assert "Paciente Fictício" not in texto
    assert not any(button.key.startswith("painel-profissional-prontuario") for button in app.button)


@pytest.mark.parametrize(
    ("status", "mensagem"),
    [(401, "Sua sessão expirou"), (403, "não tem permissão"),
     (503, "Não foi possível carregar sua agenda")],
)
def test_erros_da_api_nao_exibem_detalhes(cliente_painel, status, mensagem):
    cliente_painel.listar_consultas.side_effect = ErroAcesso("erro técnico privado", status)
    app = abrir(cliente_painel)
    texto = texto_ui(app)

    assert any(mensagem in item.value for item in app.error)
    assert "erro técnico privado" not in texto
    assert "Paciente Fictício" not in texto
    if status == 401:
        assert sessao.CHAVE not in app.session_state


def test_atalhos_existentes_navegam_para_agenda_e_prontuarios(cliente_painel):
    app = abrir(cliente_painel)
    agenda = app.button(key="painel-profissional-agenda-atalho")
    prontuario = app.button(key="painel-profissional-prontuario")

    assert agenda is not None
    assert prontuario is not None
    assert not agenda.disabled
    assert not prontuario.disabled

    app.button(key="painel-profissional-agenda-atalho").click().run()
    assert app.session_state["pagina_equipe"] == "agenda"
