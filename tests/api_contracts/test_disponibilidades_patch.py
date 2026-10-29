from datetime import timedelta
from pathlib import Path

import pytest

from conftest import FUTURO, resposta
from sorrisomais.contratos_clinicos import DadosContratoInvalidos


def test_patch_disponibilidades_altera_situacao_sem_rede_real(cliente, http):
    inicio = FUTURO.isoformat()
    fim = (FUTURO + timedelta(hours=1)).isoformat()
    http.return_value = resposta({"disponibilidade": {
        "id": 15, "profissional_id": 8, "inicio": inicio, "fim": fim,
        "situacao": "bloqueado",
    }})

    resultado = cliente.atualizar_disponibilidade(
        "token-ficticio", 15, situacao="bloqueado",
    )

    assert resultado["situacao"] == "bloqueado"
    assert resultado["inicio"] == inicio
    assert resultado["fim"] == fim
    assert http.call_args.args[:2] == (
        "PATCH", "https://exemplo.invalid/api:teste/disponibilidades/15",
    )
    assert http.call_args.kwargs["json"] == {"situacao": "bloqueado"}


@pytest.mark.parametrize("situacao", ["reservado", "indisponivel", "livre"])
def test_patch_disponibilidades_rejeita_situacao_controlada_pelo_backend(cliente, http, situacao):
    with pytest.raises(DadosContratoInvalidos):
        cliente.atualizar_disponibilidade("token-ficticio", 15, situacao=situacao)
    http.assert_not_called()


def test_patch_disponibilidades_exige_campo_sem_vazio(cliente, http):
    with pytest.raises(DadosContratoInvalidos):
        cliente.atualizar_disponibilidade("token-ficticio", 15)
    http.assert_not_called()


def test_patch_disponibilidade_revalida_estado_apos_trava_antes_de_gravar():
    """Regressão da edição que aguardava uma reserva concorrente e a sobrescrevia."""
    raiz = Path(__file__).resolve().parents[2]
    fonte = (raiz / "backend/xano/api/sorriso_acesso/disponibilidades_id_PATCH.xs").read_text(encoding="utf-8")
    assert "agenda_lock_version" not in fonte
    assert "db.edit agenda_controle" in fonte
    transacao = fonte.split("db.transaction", 1)[1]
    trava = transacao.index("} as $trava_agenda")
    releitura = transacao.index("db.get disponibilidade_agenda", trava)
    validacao = transacao.index("if ($disponibilidade_atual == null", releitura)
    escrita = transacao.index("db.edit disponibilidade_agenda", validacao)
    assert trava < releitura < validacao < escrita
    guarda = transacao[validacao:escrita]
    for campo in ("profissional_id", "inicio", "fim", "situacao"):
        assert f"$disponibilidade_atual.{campo} != $disponibilidade.{campo}" in guarda
    assert '$disponibilidade_atual.situacao == "reservado"' in guarda
    assert '$disponibilidade_atual.situacao == "indisponivel"' in guarda
    assert "$disponibilidade_atual.inicio <= now" in guarda
    assert "var.update $conflito { value = true }" in guarda
