from datetime import datetime, timedelta, timezone
from unittest.mock import Mock

from streamlit.testing.v1 import AppTest

from sorrisomais.api import ContaAcesso
from sorrisomais.acesso_equipe import renderizar


def _executar(conta, paginas):
    from sorrisomais.acesso_equipe import renderizar
    renderizar(conta, None, paginas)


def test_perfil_somente_paciente_nao_abre_area_da_equipe():
    expiracao = datetime.now(timezone.utc) + timedelta(hours=1)
    conta = ContaAcesso(12, "Paciente Fictício", ("paciente",), expiracao)
    paginas = Mock()

    app = AppTest.from_function(_executar, args=(conta, paginas)).run()

    assert not app.exception
    assert any(item.value == "Acesso da equipe" for item in app.title)
    assert any("endereço separado" in item.value for item in app.info)
    paginas.renderizar.assert_not_called()


def test_perfil_interno_continua_compondo_area_da_equipe():
    expiracao = datetime.now(timezone.utc) + timedelta(hours=1)
    conta = ContaAcesso(13, "Profissional Fictício", ("profissional",), expiracao)
    paginas = Mock()

    assert renderizar(conta, None, paginas) is True
    paginas.renderizar.assert_called_once_with(conta, None)
