import pytest
from pathlib import Path

from sorrisomais.api import ErroAcesso
from sorrisomais.contratos_clinicos import DadosContratoInvalidos
from conftest import resposta


def test_post_consultas_evitar_pipes_incompativeis_com_xano():
    raiz = Path(__file__).resolve().parents[2]
    fonte = (raiz / "backend/xano/api/sorriso_acesso/consultas_POST.xs").read_text(encoding="utf-8")
    assert " in " not in fonte
    assert "|default:" not in fonte
    assert "db.get procedimento" in fonte


def test_post_consultas_deriva_profissional_no_servidor(cliente, http):
    http.return_value = resposta({"consulta": {
        "id": 13, "paciente_id": 4, "profissional_id": 8,
        "disponibilidade_id": 3, "situacao": "Agendada",
    }}, 201)
    resultado = cliente.agendar_consulta("token-ficticio", 4, 3, [2, 5], "Avaliação")
    assert resultado["id"] == 13
    assert http.call_args.args[:2] == ("POST", "https://exemplo.invalid/api:teste/consultas")
    assert http.call_args.kwargs["json"] == {
        "paciente_id": 4, "disponibilidade_id": 3,
        "procedimento_ids": [2, 5], "motivo": "Avaliação",
    }


def test_post_consultas_rejeita_ids_duplicados_sem_rede(cliente, http):
    with pytest.raises(DadosContratoInvalidos):
        cliente.agendar_consulta("token-ficticio", 4, 3, [2, 2])
    http.assert_not_called()


def test_post_consultas_mapeia_conflito_sem_tentar_novamente(cliente, http):
    http.return_value = resposta({"codigo": "CONFLITO_AGENDA"}, 409)
    with pytest.raises(ErroAcesso) as erro:
        cliente.agendar_consulta("token-ficticio", 4, 3, [])
    assert erro.value.status == 409
    assert "horário" in str(erro.value).lower()
    assert http.call_count == 1
