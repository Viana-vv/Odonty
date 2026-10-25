from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_patch_exames_exige_profissional_ativo_e_vinculo():
    source = (ROOT / "backend/xano/api/sorriso_acesso/exames_id_situacao_PATCH.xs").read_text(encoding="utf-8-sig")
    assert 'intersect:["profissional"]' in source
    assert '$conta.situacao != "ativo"' in source
    assert "$exame.profissional_id != $profissional.id" in source


def test_patch_exames_permite_somente_transicoes_sequenciais():
    source = (ROOT / "backend/xano/api/sorriso_acesso/exames_id_situacao_PATCH.xs").read_text(encoding="utf-8-sig")
    assert '$exame.situacao == "Solicitado"' in source
    assert '$input.situacao == "Realizado"' in source
    assert '$input.situacao == "Cancelado"' in source
    assert '$input.situacao == "Não realizado"' in source
    assert '$exame.situacao == "Realizado" && $input.situacao == "Resultado disponível"' in source
    assert '"HTTP/1.1 409 Conflict"' in source


def test_patch_exames_valida_cronologia_e_resultado_antes_da_liberacao():
    source = (ROOT / "backend/xano/api/sorriso_acesso/exames_id_situacao_PATCH.xs").read_text(encoding="utf-8-sig")
    assert "$realizado_em_final < $exame.solicitado_em" in source
    assert "$realizado_em_final > now" in source
    assert '"Resultado disponível" && ($resultado_final == null' in source


def test_patch_exames_preserva_campos_omitidos_e_registra_historico_atomico():
    source = (ROOT / "backend/xano/api/sorriso_acesso/exames_id_situacao_PATCH.xs").read_text(encoding="utf-8-sig")
    transacao = source.split("db.transaction", 1)[1]
    assert "db.edit exame_situacao_historico" not in transacao
    assert "db.add exame_situacao_historico" in transacao
    assert "situacao_anterior: $exame_atual.situacao" in transacao
    assert "resultado: $resultado_final" in transacao
    assert "realizado_em: $realizado_em_final" in transacao
    assert "observacoes: $observacoes_finais" in transacao
    assert "db.edit exame_situacao_controle" in transacao
    assert "db.get exame" in transacao
    assert "versao: ($controle_situacao.versao + 1)" in transacao
    assert '"HTTP/1.1 503 Service Unavailable"' in source


def test_exame_preserva_versao_de_trava_e_tabela_de_historico_append_only():
    exame = (ROOT / "backend/xano/table/exame.xs").read_text(encoding="utf-8-sig")
    historico = (ROOT / "backend/xano/table/exame_situacao_historico.xs").read_text(encoding="utf-8-sig")
    controle = (ROOT / "backend/xano/table/exame_situacao_controle.xs").read_text(encoding="utf-8-sig")
    assert 'table exame_situacao_historico' in historico
    assert 'table exame_situacao_controle' in controle
    assert 'btree|unique' in controle and 'field: [{name: "exame_id"' in controle
    assert 'int exame_id' in historico and 'table = "exame"' in historico
    assert 'int conta_acesso_id' in historico and 'table = "conta_acesso"' in historico
