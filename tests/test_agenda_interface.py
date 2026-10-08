"""Interação da Agenda Streamlit com Xano totalmente simulado e dados fictícios."""
from copy import deepcopy
from datetime import date, datetime, time, timedelta, timezone
import json
from pathlib import Path
from unittest.mock import Mock

import pytest
from streamlit.testing.v1 import AppTest

from sorrisomais import sessao
from sorrisomais.api import ClienteXano, ContaAcesso, Credencial, ErroAcesso


FIXTURE = json.loads((Path(__file__).parent / "fixtures" / "agenda_ficticia.json").read_text(encoding="utf-8"))


@pytest.fixture
def agenda_simulada(monkeypatch):
    monkeypatch.setenv("XANO_API_BASE_URL", "https://exemplo.invalid/api:agenda-ficticia")
    monkeypatch.setenv("SORRISOMAIS_MODO_DEMONSTRACAO", "0")
    estado = {"consultas": deepcopy(FIXTURE["consultas"]),
              "disponibilidades": deepcopy(FIXTURE["disponibilidades"]),
              "criados": [], "alterados": [], "listagens": 0, "disponibilidades_criadas": [],
              "filtros_disponibilidade": []}
    validade = datetime.now(timezone.utc) + timedelta(hours=1)

    def identificar(_self, _token):
        perfil = estado.get("perfil", "recepcionista")
        return ContaAcesso(50, "Conta Fictícia Agenda", (perfil,), validade)

    monkeypatch.setattr(ClienteXano, "entrar", lambda _self, _email, _senha: Credencial("token-ficticio", validade))
    monkeypatch.setattr(ClienteXano, "identificar", identificar)
    monkeypatch.setattr(ClienteXano, "sair", lambda _self, _token: None)

    def listar(_self, _token, **_filtros):
        estado["listagens"] += 1
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
        if estado.get("erro_opcoes"):
            raise ErroAcesso("Muitas tentativas. Aguarde um pouco antes de tentar novamente.", 429)
        return deepcopy(FIXTURE["opcoes"])

    def disponibilidades(_self, _token, profissional_id=None, inicio=None, fim=None):
        estado["filtros_disponibilidade"].append((profissional_id, inicio, fim))
        return [d.copy() for d in estado["disponibilidades"]
                if d["profissional_id"] == profissional_id and d["inicio"] >= inicio and d["inicio"] < fim]

    def criar_disponibilidade(_self, _token, profissional_id, inicio, fim):
        if estado.get("erro_disponibilidade"):
            raise ErroAcesso("Não foi possível conectar ao serviço.", 503)
        if estado.get("conflito_disponibilidade"):
            raise ErroAcesso(
                "Já existe um horário sobreposto para este Profissional. Escolha outro intervalo.",
                409,
            )
        criada = {"id": 900, "profissional_id": profissional_id, "inicio": inicio,
                  "fim": fim, "situacao": "disponivel"}
        estado["disponibilidades"].append(criada)
        estado["disponibilidades_criadas"].append(criada.copy())
        return criada

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
    monkeypatch.setattr(ClienteXano, "criar_disponibilidade", criar_disponibilidade)
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
    assert not any(button.key == "agenda-novo-horario" for button in app.button)


def test_administrador_pode_iniciar_nova_consulta(agenda_simulada):
    app = abrir_agenda(agenda_simulada, "administrador")
    assert any(button.key == "agenda-nova" for button in app.button)
    assert any(button.key == "agenda-novo-horario" for button in app.button)


def test_formularios_agenda_sao_exclusivos_ao_alternar(agenda_simulada):
    app = abrir_agenda(agenda_simulada)
    app.button(key="agenda-nova").click().run()
    assert any(item.key == "agenda-consulta-data" for item in app.date_input)
    assert not any(item.key == "agenda-disponibilidade-data" for item in app.date_input)

    app.button(key="agenda-novo-horario").click().run()
    assert not any(item.key == "agenda-consulta-data" for item in app.date_input)
    assert any(item.key == "agenda-disponibilidade-data" for item in app.date_input)

    app.button(key="agenda-nova").click().run()
    assert any(item.key == "agenda-consulta-data" for item in app.date_input)
    assert not any(item.key == "agenda-disponibilidade-data" for item in app.date_input)


def test_recepcao_cadastra_disponibilidade_e_pode_usar_em_nova_consulta(agenda_simulada):
    app = abrir_agenda(agenda_simulada)
    data_futura = date.today() + timedelta(days=5)
    app.date_input(key="agenda_data_input").set_value(data_futura).run()
    app.button(key="agenda-novo-horario").click().run()

    assert app.selectbox(key="agenda-disponibilidade-profissional").options == [
        "Dra. Exemplo Sorriso",
    ]
    app.date_input(key="agenda-disponibilidade-data").set_value(data_futura)
    app.time_input(key="agenda-disponibilidade-inicio").set_value(time(14, 0))
    app.time_input(key="agenda-disponibilidade-fim").set_value(time(15, 0))
    next(button for button in app.button if button.label.startswith("Cadastrar hor")).click().run()

    assert not app.exception
    assert len(agenda_simulada["disponibilidades_criadas"]) == 1
    criada = agenda_simulada["disponibilidades_criadas"][0]
    assert criada["profissional_id"] == 201
    assert criada["inicio"].startswith(data_futura.isoformat() + "T14:00:00-03:00")
    assert any("Horário cadastrado" in item.value for item in app.success)

    app.button(key="agenda-nova").click().run()
    assert any("14:00 – 15:00" in item for item in app.selectbox(key="agenda-disponibilidade").options)


def test_formulario_sugere_intervalo_futuro_quando_data_selecionada_e_hoje(agenda_simulada):
    from zoneinfo import ZoneInfo

    app = abrir_agenda(agenda_simulada)
    hoje = date.today()
    app.date_input(key="agenda_data_input").set_value(hoje).run()
    app.button(key="agenda-novo-horario").click().run()

    data = app.date_input(key="agenda-disponibilidade-data").value
    hora_inicio = app.time_input(key="agenda-disponibilidade-inicio").value
    inicio = datetime.combine(data, hora_inicio, tzinfo=ZoneInfo("America/Sao_Paulo"))
    assert inicio > datetime.now(ZoneInfo("America/Sao_Paulo"))


def test_formulario_aceita_horario_futuro_amanha_apos_meio_dia(agenda_simulada):
    from zoneinfo import ZoneInfo

    fuso = ZoneInfo("America/Sao_Paulo")
    amanha = datetime.now(fuso).date() + timedelta(days=1)
    app = abrir_agenda(agenda_simulada)
    app.date_input(key="agenda_data_input").set_value(amanha).run()
    app.button(key="agenda-novo-horario").click().run()
    app.date_input(key="agenda-disponibilidade-data").set_value(amanha)
    app.time_input(key="agenda-disponibilidade-inicio").set_value(time(12, 33))
    app.time_input(key="agenda-disponibilidade-fim").set_value(time(14, 3))
    next(button for button in app.button if button.label.startswith("Cadastrar hor")).click().run()

    assert not any("Escolha uma data e um horÃ¡rio futuros" in item.value for item in app.error)
    assert len(agenda_simulada["disponibilidades_criadas"]) == 1


def test_formulario_mostra_data_hora_recebidas_quando_inicio_passou(agenda_simulada):
    from zoneinfo import ZoneInfo

    hoje = datetime.now(ZoneInfo("America/Sao_Paulo")).date()
    app = abrir_agenda(agenda_simulada)
    app.date_input(key="agenda_data_input").set_value(hoje).run()
    app.button(key="agenda-novo-horario").click().run()
    app.date_input(key="agenda-disponibilidade-data").set_value(hoje)
    app.time_input(key="agenda-disponibilidade-inicio").set_value(time(0, 1))
    app.time_input(key="agenda-disponibilidade-fim").set_value(time(1, 0))
    next(button for button in app.button if button.label.startswith("Cadastrar hor")).click().run()

    assert any("O início precisa ser futuro" in item.value and "formulário recebeu" in item.value
               for item in app.error)
    assert agenda_simulada["disponibilidades_criadas"] == []


def test_disponibilidade_rejeita_horario_invalido_e_exibe_conflito(agenda_simulada):
    app = abrir_agenda(agenda_simulada)
    data_futura = date.today() + timedelta(days=5)
    app.date_input(key="agenda_data_input").set_value(data_futura).run()
    app.button(key="agenda-novo-horario").click().run()
    app.date_input(key="agenda-disponibilidade-data").set_value(data_futura)
    app.time_input(key="agenda-disponibilidade-inicio").set_value(time(15, 0))
    app.time_input(key="agenda-disponibilidade-fim").set_value(time(14, 0))
    next(button for button in app.button if button.label.startswith("Cadastrar hor")).click().run()
    assert any("posterior ao horário inicial" in item.value for item in app.error)
    assert agenda_simulada["disponibilidades_criadas"] == []

    agenda_simulada["conflito_disponibilidade"] = True
    app.time_input(key="agenda-disponibilidade-inicio").set_value(time(14, 0))
    app.time_input(key="agenda-disponibilidade-fim").set_value(time(15, 0))
    next(button for button in app.button if button.label.startswith("Cadastrar hor")).click().run()
    assert any("horário sobreposto" in item.value for item in app.error)
    assert not app.success


def test_disponibilidade_exibe_indisponibilidade_sem_confirmar_sucesso(agenda_simulada):
    app = abrir_agenda(agenda_simulada)
    data_futura = date.today() + timedelta(days=5)
    app.date_input(key="agenda_data_input").set_value(data_futura).run()
    app.button(key="agenda-novo-horario").click().run()
    app.date_input(key="agenda-disponibilidade-data").set_value(data_futura)
    agenda_simulada["erro_disponibilidade"] = True
    next(button for button in app.button if button.label.startswith("Cadastrar hor")).click().run()

    assert not app.exception
    assert any("Não foi possível conectar" in item.value for item in app.error)
    assert not app.success
    assert agenda_simulada["disponibilidades_criadas"] == []


def test_recepcao_cria_consulta_ficticia_sem_requisicao_real(agenda_simulada):
    app = abrir_agenda(agenda_simulada)
    app.button(key="agenda-nova").click().run()
    assert app.date_input(key="agenda-consulta-data").value == date(2026, 10, 5)
    app.date_input(key="agenda-consulta-data").set_value(date(2026, 10, 6)).run()
    assert app.date_input(key="agenda_data_input").value == date(2026, 10, 5)
    profissional_id, inicio_disponibilidade, fim_disponibilidade = agenda_simulada["filtros_disponibilidade"][-1]
    assert profissional_id == 201
    assert inicio_disponibilidade.startswith("2026-10-06T00:00:00")
    assert fim_disponibilidade.startswith("2026-10-07T00:00:00")
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
    assert app.date_input(key="agenda_data_input").value == date(2026, 10, 6)


def test_proximo_dia_carrega_horario_e_habilita_cadastro(agenda_simulada):
    app = abrir_agenda(agenda_simulada)
    app.button(key="agenda-nova").click().run()
    enviar = next(button for button in app.button if button.label == "Agendar consulta")
    assert enviar.disabled
    assert any("Nenhum horário disponível" in item.value for item in app.info)

    app.button(key="agenda-proximo").click().run()
    assert app.date_input(key="agenda_data_input").value == date(2026, 10, 6)
    assert app.date_input(key="agenda-consulta-data").value == date(2026, 10, 5)
    app.date_input(key="agenda-consulta-data").set_value(date(2026, 10, 6)).run()
    assert app.date_input(key="agenda_data_input").value == date(2026, 10, 6)
    assert app.selectbox(key="agenda-disponibilidade").options == ["10:00 – 10:45"]
    enviar = next(button for button in app.button if button.label == "Agendar consulta")
    assert not enviar.disabled


def test_agendamento_exibe_mensagem_de_limite_de_tentativas(agenda_simulada):
    agenda_simulada["erro_opcoes"] = True
    app = abrir_agenda(agenda_simulada)
    app.button(key="agenda-nova").click().run()

    assert any("Muitas tentativas" in item.value for item in app.error)
    assert not any("Não foi possível carregar as opções" in item.value for item in app.error)


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


def test_profissional_atualiza_consulta_sem_recarregar_lista_duas_vezes(agenda_simulada):
    app = abrir_agenda(agenda_simulada, "profissional")
    consultas_antes = agenda_simulada["listagens"]

    app.button(key="agenda-atualizar-502").click().run()

    assert not app.exception
    assert agenda_simulada["alterados"] == [(502, "Em atendimento", None)]
    assert agenda_simulada["listagens"] == consultas_antes + 1
    assert app.selectbox(key="agenda-proxima-502").options == ["Realizada"]
    assert sum("Paciente Fictício Horizonte" in item.value for item in app.markdown) == 1
    assert sum("Paciente Fictícia Aurora" in item.value for item in app.markdown) == 1
