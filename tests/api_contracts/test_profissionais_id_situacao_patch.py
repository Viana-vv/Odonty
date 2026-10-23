from pathlib import Path

import pytest

from sorrisomais.api import ErroAcesso
from conftest import resposta


@pytest.mark.parametrize("situacao", ["ativo", "inativo"])
def test_patch_profissional_atualiza_situacao(cliente, http, situacao):
    http.return_value = resposta({"profissional": {"id": 201, "situacao": situacao}})
    assert cliente.atualizar_situacao_profissional("token-ficticio", 201, situacao) == {
        "id": 201, "situacao": situacao,
    }
    assert http.call_args.args[:2] == ("PATCH", "https://exemplo.invalid/api:teste/profissionais/201/situacao")
    assert http.call_args.kwargs["json"] == {"situacao": situacao}


def test_patch_profissional_rejeita_situacao_invalida_sem_rede(cliente, http):
    with pytest.raises(ErroAcesso):
        cliente.atualizar_situacao_profissional("token-ficticio", 201, "afastado")
    http.assert_not_called()


def test_patch_profissional_rejeita_identificador_invalido_sem_rede(cliente, http):
    with pytest.raises(ErroAcesso) as erro:
        cliente.atualizar_situacao_profissional("token-ficticio", 0, "inativo")
    assert erro.value.status == 400
    http.assert_not_called()


def test_patch_profissional_mapeia_recepcionista_sem_permissao(cliente, http):
    http.return_value = resposta({"codigo": "ACESSO_NEGADO"}, 403)
    with pytest.raises(ErroAcesso) as erro:
        cliente.atualizar_situacao_profissional("token-ficticio", 201, "inativo")
    assert erro.value.status == 403


def test_export_patch_exclusivo_admin_e_edita_somente_situacao():
    path = Path(__file__).resolve().parents[2] / "backend/xano/api/sorriso_acesso/profissionais_id_situacao_PATCH.xs"
    source = path.read_text(encoding="utf-8-sig")
    assert 'intersect:["administrador"]' in source
    assert '($bruto|keys|count) != 1' in source
    assert 'situacao: $situacao_armazenada' in source
    assert 'atualizado_em: now' in source
    assert "db.delete" not in source.lower()


def test_profissional_inativo_permanece_bloqueado_para_novos_agendamentos():
    path = Path(__file__).resolve().parents[2] / "backend/xano/api/sorriso_acesso/consultas_POST.xs"
    source = path.read_text(encoding="utf-8-sig")
    assert '$profissional.situacao != "Ativo"' in source
    assert "CONFLITO_AGENDA" in source
