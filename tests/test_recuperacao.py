import pytest

from sorrisomais.api import ErroAcesso
from sorrisomais.recuperacao import montar_otp, validar_email, validar_otp, validar_senhas


def test_validadores_normalizam_email_e_otp():
    assert validar_email(" Pessoa@Example.com ") == "pessoa@example.com"
    assert validar_otp(" 123456 ") == "123456"


def test_montar_otp_concatena_campos_individuais():
    assert montar_otp(["1", "2", "3", "4", "5", "6"]) == "123456"
    assert montar_otp(["1", None, "3", "", "5", "6"]) == "1356"


@pytest.mark.parametrize("otp", ["", "12345", "1234567", "abcdef"])
def test_otp_deve_ter_seis_digitos(otp):
    with pytest.raises(ErroAcesso):
        validar_otp(otp)


def test_senhas_devem_ser_iguais_e_fortes():
    senha = "senha-ficticia-segura"
    assert validar_senhas(senha, senha) == senha
    with pytest.raises(ErroAcesso):
        validar_senhas(senha, "outra-senha-ficticia")
