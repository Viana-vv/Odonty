"""Contratos de criação de seções do Prontuário sem chamadas reais ao Xano."""

from pathlib import Path
import pytest

from conftest import resposta
from sorrisomais.contratos_clinicos import DadosContratoInvalidos


def test_post_secao_prontuario_envia_tipo_conteudo_e_vinculo(cliente, http):
    http.return_value = resposta({"secao": {
        "id": 41,
        "prontuario_id": 30,
        "paciente_id": 12,
        "tipo": "anamnese",
        "versao": 1,
        "conteudo": '{"alergias": "Nenhuma fictícia"}',
    }}, 201)

    resultado = cliente.registrar_secao_prontuario(
        "token-ficticio", 12, "anamnese",
        {"alergias": "Nenhuma fictícia"}, consulta_id=9,
    )

    assert resultado["id"] == 41
    assert http.call_args.args[:2] == (
        "POST", "https://exemplo.invalid/api:teste/prontuarios/12/secoes",
    )
    assert http.call_args.kwargs["json"] == {
        "tipo": "anamnese",
        "conteudo": '{"alergias": "Nenhuma fictícia"}',
        "consulta_id": 9,
        "liberado_paciente": False,
    }


@pytest.mark.parametrize("tipo", ["", "secao-inexistente", None])
def test_post_secao_prontuario_rejeita_tipo_invalido_sem_rede(cliente, http, tipo):
    with pytest.raises(DadosContratoInvalidos):
        cliente.registrar_secao_prontuario("token-ficticio", 12, tipo, {})

    http.assert_not_called()


def test_post_secao_prontuario_rejeita_conteudo_vazio_sem_rede(cliente, http):
    with pytest.raises(DadosContratoInvalidos):
        cliente.registrar_secao_prontuario(
            "token-ficticio", 12, "anamnese", {},
        )

    http.assert_not_called()


def test_post_secao_prontuario_rejeita_vinculo_invalido_sem_rede(cliente, http):
    with pytest.raises(DadosContratoInvalidos):
        cliente.registrar_secao_prontuario(
            "token-ficticio", 0, "diagnosticos", {"descricao": "Fictício"},
        )

    http.assert_not_called()


def test_post_secao_prontuario_exige_validacao_de_sessao_escopo_e_historico():
    caminho = (Path(__file__).resolve().parents[2] / "backend" / "xano" / "api"
               / "sorriso_acesso" / "prontuarios_id_secoes_POST.xs")
    codigo = caminho.read_text(encoding="utf-8-sig")

    assert 'auth = "conta_acesso"' in codigo
    assert "function.run sorriso_validar_sessao" in codigo
    assert '"profissional"' in codigo
    assert "$input.paciente_id" in codigo
    assert "$bruto.consulta_id" in codigo
    assert "versao" in codigo
    assert "history = false" in codigo


def test_post_secao_prontuario_nao_permite_exclusao_fisica_ou_log_clinico():
    caminho = (Path(__file__).resolve().parents[2] / "backend" / "xano" / "api"
               / "sorriso_acesso" / "prontuarios_id_secoes_POST.xs")
    codigo = caminho.read_text(encoding="utf-8-sig")

    assert "db.delete" not in codigo
    assert "log(" not in codigo.lower()
