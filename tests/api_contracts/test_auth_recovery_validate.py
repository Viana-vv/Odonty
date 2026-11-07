from pathlib import Path


def test_xano_valida_otp_com_limite_e_expiracao():
    caminho = Path(__file__).resolve().parents[2] / "backend/xano/api/sorriso_acesso/auth/recuperacao-senha-validar_POST.xs"
    codigo = caminho.read_text(encoding="utf-8-sig")
    assert "security.check_password" in codigo
    assert "tentativas >= 5" in codigo
    assert "expira_em <= now" in codigo
    assert "validado: true" in codigo
