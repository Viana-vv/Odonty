"""Interação da Agenda Streamlit com Xano totalmente simulado e dados fictícios."""
from copy import deepcopy
from datetime import date, datetime, timedelta, timezone
import json
from pathlib import Path
from unittest.mock import Mock

import pytest
from streamlit.testing.v1 import AppTest

from sorrisomais import sessao
from sorrisomais.api import ClienteXano, ContaAcesso, Credencial


FIXTURE = json.loads((Path(__file__).parent / "fixtures" / "agenda_ficticia.json").read_text(encoding="utf-8"))


@pytest.fixture
def agenda_simulada(monkeypatch):
    monkeypatch.setenv("XANO_API_BASE_URL", "https://exemplo.invalid/api:agenda-ficticia")
    monkeypatch.setenv("SORRISOMAIS_MODO_DEMONSTRACAO", "0")
    estado = {"consultas": deepcopy(FIXTURE["consultas"]), "criados": [], "alterados": []}
    validade = datetime.now(timezone.utc) + timedelta(hours=1)

    def identificar(_self, _token):
        perfil = estado.get("perfil", "recepcionista")
        return ContaAcesso(50, "Conta Fictícia Agenda", (perfil,), validade)

    monkeypatch.setattr(ClienteXano, "entrar", lambda _self, _email, _senha: Credencial("token-ficticio", validade))
    monkeypatch.setattr(ClienteXano, "identificar", identificar)
    monkeypatch.setattr(ClienteXano, "sair", lambda _self, _token: None)

    def listar(_self, _token, **_filtros):
        # O adaptador real já elimina linhas repetidas de Consulta e agrega seus Procedimentos.
        consultas = {}
        for linha in estado["consultas"]:
            atual = consultas.setdefault(linha["id"], {k: v for k, v in linha.items()
                if k not in {"procedimento_nome", "procedimento_vinculado_nome"}} | {"procedimentos": []})
            for chave in ("procedimento_nome", "procedimento_vinculado_nome"):
                nome = linha.get(chave)
                if nome and nome not in atual["procedimentos"]:
                    atual["procedimentos"].append(nome)
        return list(consultas.values())

    def opcoes(_self, _token):
        return deepcopy(FIXTURE["opcoes"])

    def disponibilidades(_self, _token, profissional_id=None, inicio=None, fim=None):
        return [d.copy() for d in FIXTURE["disponibilidades"]
                if d["profissional_id"] == profissional_id and d["inicio"] >= inicio and d["inicio"] < fim]

    def agendar(_self, _token, paciente_id, disponibilidade_id, procedimento_ids, motivo=None):
        disponibilidade = next(d for d in FIXTURE["disponibilidades"] if d["id"] == disponibilidade_id)
        novos = {
            "id": 503, "paciente_id": paciente_id, "profissional_id": disponibilidade["profissional_id"],
            "disponibilidade_id": disponibilidade_id, "situacao": "Agendada",
            "inicio_em": disponibilidade["inicio"], "fim_em": disponibilidade["fim"],
            "paciente_nome": next(p["nome"] for p in FIXTURE["opcoes"]["pacientes"] if p["id"] == paciente_id),
            "profissional_nome": next(p["nome"] for p in FIXTURE["opcoes"]["profissionais"] if p["id"] == disponibilidade["profissional_id"]),
            "procedimentos": [p["nome"] for p in FIXTURE["opcoes"]["procedimentos"] if p["id"] in procedimento_ids],
        }
        estado["criados"].append({"consulta": novos, "motivo": motivo})
        estado["consultas"].append(novos)
        return novos

    def atualizar(_self, _token, consulta_id, nova, motivo_cancelamento=None):
        estado["alterados"].append((consulta_id, nova, motivo_cancelamento))
        for c in estado["consultas"]:
            if c["id"] == consulta_id:
                c["situacao"] = nova
        return {"id": consulta_id, "situacao": nova}

    monkeypatch.setattr(ClienteXano, "listar_consultas", listar)
    monkeypatch.setattr(ClienteXano, "listar_opcoes_agenda", opcoes)
    monkeypatch.setattr(ClienteXano, "listar_disponibilidades", disponibilidades)
    monkeypatch.setattr(ClienteXano, "agendar_consulta", agendar)
    monkeypatch.setattr(ClienteXano, "atualizar_situacao_consulta", atualizar)
    return estado


def abrir_agenda(agenda_simulada, perfil="recepcionista"):
    agenda_simulada["perfil"] = perfil
    app = AppTest.from_file(Path(__file__).resolve().parents[1] / "app.py", default_timeout=30).run()
    app.session_state["agenda_data"] = date.fromisoformat(FIXTURE["data"])
    app.text_input(key="email").set_value("equipe.ficticia@example.invalid")
    app.text_input(key="senha").set_value("senha-local-ficticia")
    app.button(key="login-entrar").click().run()
    app.button(key="menu-agenda").click().run()
    assert not app.exception
    return app


def test_recepcao_visualiza_agenda_e_filtra_por_situacao(agenda_simulada):
    app = abrir_agenda(agenda_simulada)
    assert any(item.value == "Agenda" for item in app.title)
    assert not any("Aqui está um resumo" in item.value for item in app.caption)
    assert any("Paciente Fictícia Aurora" in item.value for item in app.markdown)
    assert any("Profilaxia fictícia" in item.value for item in app.caption)

    app.selectbox(key="agenda_situacao").select("Confirmada").run()
    assert any("Paciente Fictício Horizonte" in item.value for item in app.markdown)
    assert not any("Paciente Fictícia Aurora" in item.value for item in app.markdown)


def test_profissional_consulta_agenda_sem_acao_de_criar(agenda_simulada):
    app = abrir_agenda(agenda_simulada, "profissional")
    assert app.button(key="menu-agenda")
    assert not any(button.key == "agenda-nova" for button in app.button)
    assert app.selectbox(key="agenda-proxima-502").options == ["Em atendimento", "Cancelada", "Falta"]


def test_administrador_pode_iniciar_nova_consulta(agenda_simulada):
    app = abrir_agenda(agenda_simulada, "administrador")
    assert any(button.key == "agenda-nova" for button in app.button)


def test_recepcao_cria_consulta_ficticia_sem_requisicao_real(agenda_simulada):
    app = abrir_agenda(agenda_simulada)
    app.date_input(key="agenda_data_input").set_value(date(2026, 10, 6)).run()
    app.button(key="agenda-nova").click().run()
    assert app.selectbox(key="agenda-paciente").options == [
        "Paciente Fictícia Aurora", "Paciente Fictício Horizonte",
    ]
    app.selectbox(key="agenda-paciente").select(102)
    app.selectbox(key="agenda-profissional").select(201)
    app.selectbox(key="agenda-disponibilidade").select(403)
    app.multiselect(key="agenda-procedimentos").select(301).select(302)
    app.text_area(key="agenda-motivo-nova").set_value("Motivo administrativo fictício")
    submit = next(button for button in app.button if button.label == "Agendar consulta")
    submit.click().run()
    assert not app.exception
    assert len(agenda_simulada["criados"]) == 1
    criada = agenda_simulada["criados"][0]
    assert criada["consulta"]["procedimentos"] == ["Avaliação fictícia", "Profilaxia fictícia"]
    assert criada["motivo"] == "Motivo administrativo fictício"
    assert any(item.value == "Consulta agendada." for item in app.success)


def test_proximo_dia_carrega_horario_e_habilita_cadastro(agenda_simulada):
    app = abrir_agenda(agenda_simulada)
    app.button(key="agenda-nova").click().run()
    enviar = next(button for button in app.button if button.label == "Agendar consulta")
    assert enviar.disabled
    assert any("Nenhum horário disponível" in item.value for item in app.info)

    app.button(key="agenda-proximo").click().run()
    assert app.date_input(key="agenda_data_input").value == date(2026, 10, 6)
    assert app.selectbox(key="agenda-disponibilidade").options == ["10:00 – 10:45"]
    enviar = next(button for button in app.button if button.label == "Agendar consulta")
    assert not enviar.disabled


def test_cancelamento_exige_motivo_e_confirmacao(agenda_simulada):
    app = abrir_agenda(agenda_simulada)
    app.selectbox(key="agenda-proxima-501").select("Cancelada")
    app.run()
    assert not app.text_input(key="agenda-motivo-501").disabled
    app.button(key="agenda-atualizar-501").click().run()
    assert agenda_simulada["alterados"] == []
    app.text_input(key="agenda-motivo-501").set_value("Solicitação fictícia")
    app.checkbox(key="agenda-confirmar-501").check()
    submit = app.button(key="agenda-atualizar-501")
    submit.click().run()
    assert not app.exception
    assert agenda_simulada["alterados"] == [(501, "Cancelada", "Solicitação fictícia")]
