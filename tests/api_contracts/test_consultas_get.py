from datetime import timedelta
import json
from pathlib import Path
import re

import pytest

from conftest import FUTURO, resposta
from sorrisomais.api import ErroAcesso


def agenda_ficticia():
    return json.loads((Path(__file__).parents[1] / "fixtures" / "agenda_ficticia.json").read_text(encoding="utf-8"))


def test_get_consultas_envia_filtros_e_resposta_sem_dados_extras(cliente, http):
    inicio = FUTURO.isoformat()
    fim = (FUTURO + timedelta(hours=1)).isoformat()
    consulta = agenda_ficticia()["consultas"][0] | {
        "telefone": "FICTICIO-NAO-EXIBIR", "conteudo_clinico": "CONTEUDO FICTICIO NAO EXIBIR"
    }
    http.return_value = resposta({"consultas": [consulta]})
    resultado = cliente.listar_consultas(
        "token-ficticio", paciente_id=101, profissional_id=201, situacao="Agendada", inicio=inicio, fim=fim,
    )
    assert resultado == [{
        "id": 501, "paciente_id": 101, "profissional_id": 201, "disponibilidade_id": 401,
        "situacao": "Agendada", "inicio_em": "2026-10-05T13:00:00-03:00",
        "fim_em": "2026-10-05T13:45:00-03:00", "paciente_nome": "Paciente Fictícia Aurora",
        "profissional_nome": "Dra. Exemplo Sorriso", "procedimentos": ["Avaliação fictícia"],
    }]
    assert http.call_args.args[:2] == ("GET", "https://exemplo.invalid/api:teste/consultas")
    assert http.call_args.kwargs["params"] == {
        "paciente_id": 101, "profissional_id": 201, "situacao": "Agendada", "inicio": inicio, "fim": fim,
    }


def test_get_consultas_agrega_procedimentos_sem_repetir_consulta(cliente, http):
    http.return_value = resposta({"consultas": agenda_ficticia()["consultas"]})
    resultado = cliente.listar_consultas("token-ficticio")
    assert len(resultado) == 2
    assert resultado[0]["procedimentos"] == ["Avaliação fictícia", "Profilaxia fictícia"]
    assert resultado[1]["procedimentos"] == []


def test_get_consultas_rejeita_resposta_sem_rotulos(cliente, http):
    http.return_value = resposta({"consultas": [{
        "id": 9, "paciente_id": 4, "profissional_id": 8, "situacao": "Agendada",
        "inicio_em": "inválido", "fim_em": "inválido",
    }]})
    with pytest.raises(ErroAcesso):
        cliente.listar_consultas("token-ficticio")


def test_get_consultas_aceita_resposta_minima_do_paciente_sem_procedimentos(cliente, http):
    consulta_minima = {
        "id": 501,
        "paciente_id": 101,
        "profissional_id": 201,
        "inicio_em": "2026-10-05T16:00:00+00:00",
        "fim_em": "2026-10-05T16:45:00+00:00",
        "situacao": "Agendada",
        "profissional_nome": "Dra. Exemplo Sorriso",
    }
    http.return_value = resposta({"consultas": [consulta_minima]})

    resultado = cliente.listar_consultas("token-ficticio")

    assert resultado == [{
        **consulta_minima,
        "disponibilidade_id": None,
        "procedimentos": [],
    }]


def test_get_consultas_serializa_paciente_sem_campos_de_procedimento():
    fonte = (Path(__file__).parents[2] / "backend" / "xano" / "api" / "sorriso_acesso" / "consultas_GET.xs").read_text(encoding="utf-8")
    inicio_serializacao = fonte.index("var $fim_iso")
    inicio_ramo = fonte.index('if (($solicitante.perfis|intersect:["paciente"]|count) > 0) {', inicio_serializacao)
    fim_ramo = fonte.index("\n          else {", inicio_ramo)
    ramo_paciente = fonte[inicio_ramo:fim_ramo]
    assert "profissional_nome:" in ramo_paciente
    assert not re.search(r"procedimento|disponibilidade_id|paciente_nome|telefone|cpf|conteudo_clinico", ramo_paciente, re.I)
    assert "procedimento_vinculado_nome" in fonte
