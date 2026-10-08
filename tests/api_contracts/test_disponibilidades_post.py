from datetime import timedelta
from pathlib import Path

import pytest

from conftest import FUTURO, resposta
from sorrisomais.api import ErroAcesso


def test_post_disponibilidades_cria_intervalo(cliente, http):
    inicio = FUTURO.isoformat()
    fim = (FUTURO + timedelta(hours=1)).isoformat()
    http.return_value = resposta({"disponibilidade": {
        "id": 15, "profissional_id": 8, "inicio": inicio, "fim": fim, "situacao": "disponivel",
    }}, 201)
    resultado = cliente.criar_disponibilidade("token-ficticio", 8, inicio, fim)
    assert resultado["id"] == 15
    assert resultado["inicio"] == inicio
    assert resultado["fim"] == fim
    assert http.call_args.args[:2] == ("POST", "https://exemplo.invalid/api:teste/disponibilidades")
    assert http.call_args.kwargs["json"] == {"profissional_id": 8, "inicio": inicio, "fim": fim}


def test_post_disponibilidades_completa_campos_omitidos_pela_api(cliente, http):
    inicio = FUTURO.isoformat()
    fim = (FUTURO + timedelta(hours=1)).isoformat()
    http.return_value = resposta({"disponibilidade": {
        "id": 16, "profissional_id": 8, "inicio": inicio,
    }}, 201)
    resultado = cliente.criar_disponibilidade("token-ficticio", 8, inicio, fim)
    assert resultado == {
        "id": 16, "profissional_id": 8, "inicio": inicio,
        "fim": fim, "situacao": "disponivel",
    }


def test_post_disponibilidades_rejeita_intervalo_invalido_sem_rede(cliente, http):
    from sorrisomais.contratos_clinicos import DadosContratoInvalidos
    import pytest

    with pytest.raises(DadosContratoInvalidos):
        cliente.criar_disponibilidade("token-ficticio", 8, "2026-10-05T10:00:00-03:00", "2026-10-05T09:00:00-03:00")
    http.assert_not_called()


def test_post_disponibilidades_mapeia_conflito_sem_rede(cliente, http):
    http.return_value = resposta({"codigo": "CONFLITO_AGENDA"}, 409)
    with pytest.raises(ErroAcesso, match="horário sobreposto") as erro:
        cliente.criar_disponibilidade(
            "token-ficticio", 8, FUTURO.isoformat(),
            (FUTURO + timedelta(hours=1)).isoformat(),
        )
    assert erro.value.status == 409
    assert http.call_count == 1


def test_post_disponibilidades_explica_rejeicao_do_xano(cliente, http):
    http.return_value = resposta({"codigo": "DADOS_INVALIDOS"}, 400)
    with pytest.raises(ErroAcesso, match="Xano recusou o intervalo") as erro:
        cliente.criar_disponibilidade(
            "token-ficticio", 8, FUTURO.isoformat(),
            (FUTURO + timedelta(hours=1)).isoformat(),
        )
    assert erro.value.status == 400


def test_post_disponibilidades_rejeita_resposta_incompativel(cliente, http):
    from datetime import datetime, timezone

    inicio = (datetime.now(timezone.utc) + timedelta(days=1)).replace(microsecond=0).isoformat()
    fim = (datetime.now(timezone.utc) + timedelta(days=1, hours=1)).replace(microsecond=0).isoformat()
    http.return_value = resposta({"disponibilidade": {"id": 20}}, 201)
    with pytest.raises(ErroAcesso):
        cliente.criar_disponibilidade("token-ficticio", 8, inicio, fim)
    assert http.call_count == 1


def test_export_post_disponibilidades_valida_sessao_perfis_e_conflito():
    caminho = (Path(__file__).resolve().parents[2] / "backend" / "xano" / "api"
               / "sorriso_acesso" / "disponibilidades_POST.xs")
    codigo = caminho.read_text(encoding="utf-8-sig")
    assert 'auth = "conta_acesso"' in codigo
    assert "function.run sorriso_validar_sessao" in codigo
    assert 'perfis|intersect:["profissional", "administrador", "recepcionista"]' in codigo
    assert "timestamp inicio?" in codigo and "timestamp fim?" in codigo
    assert "$input.inicio >= $input.fim" in codigo
    assert "$input.inicio <= now" in codigo
    assert "db.query agenda_controle" in codigo
    assert "agenda_lock_version" not in codigo
    assert '"HTTP/1.1 409 Conflict"' in codigo
    assert 'var.update $falha_servico { value = true }' in codigo
    assert 'if ($falha_servico || $criada == null)' in codigo
    assert "|default:" not in codigo
