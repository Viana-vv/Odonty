import pytest

from sorrisomais.config import Configuracao


@pytest.mark.parametrize("valor,habilitada,valida", [
    (None, False, True), ("0", False, True), ("false", False, True),
    ("1", True, True), (" TRUE ", True, True), ("sim", False, False),
])
def test_flag_fechada_por_padrao_sem_inutilizar_cliente(monkeypatch, valor, habilitada, valida):
    monkeypatch.setenv("XANO_API_BASE_URL", "https://exemplo.invalid/api:teste")
    if valor is None:
        monkeypatch.delenv("SORRISO_REDEFINICAO_HABILITADA", raising=False)
    else:
        monkeypatch.setenv("SORRISO_REDEFINICAO_HABILITADA", valor)
    config = Configuracao.do_ambiente()
    assert config.redefinicao_senha_habilitada is habilitada
    assert config.redefinicao_senha_configuracao_valida is valida
    assert config.api_base_url == "https://exemplo.invalid/api:teste"


def test_construtor_existente_permanece_desligado():
    assert not Configuracao("https://exemplo.invalid/api:teste").redefinicao_senha_habilitada
