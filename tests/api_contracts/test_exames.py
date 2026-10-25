from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_exports_exames_declaram_auth_e_sem_anexos():
    for nome in ("exames_GET.xs", "exames_POST.xs", "exames_id_situacao_PATCH.xs"):
        source = (ROOT / "backend/xano/api/sorriso_acesso" / nome).read_text(encoding="utf-8-sig")
        assert 'auth = "conta_acesso"' in source
        assert "function.run sorriso_validar_sessao" in source
        assert "arquivo" not in source and "url_publica" not in source


def test_get_exames_restringe_paciente_ao_resultado_disponivel():
    source = (ROOT / "backend/xano/api/sorriso_acesso/exames_GET.xs").read_text(encoding="utf-8-sig")
    assert 'field_name = "conta_acesso_id"' in source
    assert 'field_value = $auth.id' in source
    assert '$db.exame.paciente_id == $paciente_autenticado.id' in source
    assert 'situacao == "Resultado disponível"' in source
    assert 'resultado: $resultado_liberado' in source
    assert '$db.exame.profissional_id == $profissional.id' in source
    assert 'intersect:["profissional", "paciente"]' in source
    assert '$input.paciente_id > 0' in source
    assert '$input.consulta_id > 0' in source


def test_post_exames_exige_vinculo_com_consulta():
    source = (ROOT / "backend/xano/api/sorriso_acesso/exames_POST.xs").read_text(encoding="utf-8-sig")
    assert "$consulta.paciente_id != $paciente.id" in source
    assert "$consulta.profissional_id != $profissional.id" in source
    assert "$input.solicitado_em > now" in source
    assert "db.add exame_situacao_controle" in source
    assert "db.add exame_situacao_historico" in source
