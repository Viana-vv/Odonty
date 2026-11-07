import pytest

from sorrisomais.api import ErroAcesso
from sorrisomais.recuperacao import validar_email, validar_otp, validar_senhas


def test_validadores_normalizam_email_e_otp():
    assert validar_email(" Pessoa@Example.com ") == "pessoa@example.com"
    assert validar_otp(" 123456 ") == "123456"


@pytest.mark.parametrize("otp", ["", "12345", "1234567", "abcdef"])
def test_otp_deve_ter_seis_digitos(otp):
    with pytest.raises(ErroAcesso):
        validar_otp(otp)


def test_senhas_devem_ser_iguais_e_fortes():
    senha = "senha-ficticia-segura"
    assert validar_senhas(senha, senha) == senha
    with pytest.raises(ErroAcesso):
        validar_senhas(senha, "outra-senha-ficticia")
