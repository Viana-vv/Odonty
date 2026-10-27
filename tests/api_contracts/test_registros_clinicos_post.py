import pytest
from pathlib import Path

from conftest import resposta
from sorrisomais.contratos_clinicos import DadosContratoInvalidos


def test_post_registros_clinicos_nao_registra_payload_em_logs(cliente, http):
    http.return_value = resposta({"registro_clinico": {
        "id": 2, "paciente_id": 4, "profissional_id": 8, "prontuario_id": 6,
        "liberado_paciente": False,
    }}, 201)
    resultado = cliente.registrar_clinico(
        "token-ficticio", 4, "Evolução fictícia", consulta_id=9,
    )
    assert resultado["id"] == 2
    assert http.call_args.args[:2] == (
        "POST", "https://exemplo.invalid/api:teste/registros-clinicos",
    )
    assert http.call_args.kwargs["json"] == {
        "paciente_id": 4, "consulta_id": 9,
        "conteudo": "Evolução fictícia", "liberado_paciente": False,
    }


def test_post_registros_clinicos_rejeita_conteudo_vazio_sem_rede(cliente, http):
    with pytest.raises(DadosContratoInvalidos):
        cliente.registrar_clinico("token-ficticio", 4, "   ")
    http.assert_not_called()


def test_post_registros_clinicos_sem_consulta_explicita_exige_vinculo_profissional_paciente():
    caminho = (Path(__file__).resolve().parents[2] / "backend" / "xano" / "api"
               / "sorriso_acesso" / "registros_clinicos_POST.xs")
    codigo = caminho.read_text(encoding="utf-8-sig")
    assert '($solicitante.perfis|includes:"profissional") == false' in codigo
    assert "db.query consulta" in codigo
    assert "$db.consulta.paciente_id == $paciente.id && $db.consulta.profissional_id == $profissional.id" in codigo
    assert 'if ($consulta_escopo == null)' in codigo
