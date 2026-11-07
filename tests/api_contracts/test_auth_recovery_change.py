from pathlib import Path


def test_xano_troca_senha_e_invalida_operacao():
    caminho = Path(__file__).resolve().parents[2] / "backend/xano/api/sorriso_acesso/auth/recuperacao-senha-trocar_POST.xs"
    codigo = caminho.read_text(encoding="utf-8-sig")
    assert "db.edit conta_acesso" in codigo
    assert "senha: $input.senha" in codigo
    assert "utilizado: true" in codigo
