from datetime import date, timedelta

import pytest

from sorrisomais.demonstracao import RepositorioDemonstracao


def criar_repositorio(hoje=None):
    return RepositorioDemonstracao({}, hoje=hoje or date.today())


def test_repositorio_inicializa_dados_ficticios_relacionados_na_sessao():
    estado = {}
    repositorio = RepositorioDemonstracao(estado, hoje=date(2026, 10, 1))

    paciente = next(p for p in repositorio.listar("pacientes") if p["id"] == 1)
    registro = next(r for r in repositorio.listar("registros_clinicos") if r["paciente_id"] == 1)
    assert registro["prontuario_id"] == paciente["prontuario_id"]
    assert repositorio.listar("consultas")[0]["data"] == "2026-10-01"
    assert "sorrisomais_demo_dados" in estado


def test_repositorio_nao_expoe_mutacao_direta_das_listas():
    repositorio = criar_repositorio()
    pacientes = repositorio.listar("pacientes")
    pacientes.clear()
    assert len(repositorio.listar("pacientes")) == 3


def test_pesquisa_paciente_e_criacao_de_prontuario():
    repositorio = criar_repositorio()
    paciente_id = repositorio.salvar_paciente({
        "nome": "Paciente Fictício", "cpf": "000.000.000-99", "nascimento": "2000-01-01",
        "telefone": "(11) 90000-0099", "email": "ficticio@example.com",
    })

    novo = next(p for p in repositorio.buscar_pacientes("fictício") if p["id"] == paciente_id)
    assert novo["prontuario_id"] == 4
    assert repositorio.buscar_pacientes("inexistente") == []


def test_edicao_paciente_preserva_id_e_prontuario():
    repositorio = criar_repositorio()
    paciente = repositorio.listar("pacientes")[0]
    repositorio.salvar_paciente({"nome": "Nome Atualizado", "cpf": paciente["cpf"]}, paciente["id"])
    atualizado = next(p for p in repositorio.listar("pacientes") if p["id"] == paciente["id"])
    assert atualizado["nome"] == "Nome Atualizado"
    assert atualizado["prontuario_id"] == paciente["prontuario_id"]


def test_nao_permite_cpf_duplicado_ou_nome_invalido():
    repositorio = criar_repositorio()
    with pytest.raises(ValueError, match="já está cadastrado"):
        repositorio.salvar_paciente({"nome": "Outro Fictício", "cpf": "000.000.000-01"})
    with pytest.raises(ValueError, match="nome completo"):
        repositorio.salvar_paciente({"nome": "A", "cpf": "000.000.000-99"})


def test_profissional_pode_ser_inativado_sem_apagar_historico():
    repositorio = criar_repositorio()
    total_consultas = len(repositorio.listar("consultas"))
    repositorio.alterar_situacao_profissional(1, False)
    assert len(repositorio.listar("consultas")) == total_consultas
    assert next(p for p in repositorio.listar("profissionais") if p["id"] == 1)["situacao"] == "inativo"


def test_agendamento_rejeita_sobreposicao_de_profissional_e_paciente():
    repositorio = criar_repositorio()
    amanha = (date.today() + timedelta(days=2)).isoformat()
    repositorio.agendar_consulta(1, 1, 2, amanha, "09:00")
    with pytest.raises(ValueError, match="conflita"):
        repositorio.agendar_consulta(2, 1, 1, amanha, "09:30")
    with pytest.raises(ValueError, match="já tem uma Consulta"):
        repositorio.agendar_consulta(1, 2, 1, amanha, "09:15")


def test_agendamento_nao_aceita_profissional_inativo():
    repositorio = criar_repositorio()
    repositorio.alterar_situacao_profissional(1, False)
    amanha = (date.today() + timedelta(days=1)).isoformat()
    with pytest.raises(ValueError, match="inativo"):
        repositorio.agendar_consulta(1, 1, 1, amanha, "10:00")


def test_consulta_evolucao_e_metricas_sao_atualizados():
    repositorio = criar_repositorio()
    amanha = (date.today() + timedelta(days=1)).isoformat()
    consulta_id = repositorio.agendar_consulta(1, 1, 1, amanha, "15:00")
    repositorio.alterar_situacao_consulta(consulta_id, "Confirmada")
    registro_id = repositorio.registrar_evolucao(
        {"profissional"}, 1, 1, amanha, "Avaliação", "Evolução fictícia.",
    )
    registro = next(r for r in repositorio.listar("registros_clinicos") if r["id"] == registro_id)
    assert registro["prontuario_id"] == 1
    assert next(c for c in repositorio.listar("consultas") if c["id"] == consulta_id)["situacao"] == "Confirmada"
    assert repositorio.metricas(date.today())["pacientes"] == 3


def test_dados_clinicos_sao_restritos_a_profissional():
    repositorio = criar_repositorio()
    assert repositorio.listar_registros_clinicos({"profissional"})
    with pytest.raises(PermissionError):
        repositorio.listar_registros_clinicos({"recepcionista"})
    with pytest.raises(PermissionError):
        repositorio.registrar_evolucao({"administrador"}, 1, 1, date.today(), "Avaliação", "Fictício.")


def test_historico_pode_ser_filtrado_por_paciente():
    repositorio = criar_repositorio()
    registros = repositorio.listar_registros_clinicos({"profissional"}, paciente_id=1)
    assert registros
    assert all(r["paciente_id"] == 1 for r in registros)
