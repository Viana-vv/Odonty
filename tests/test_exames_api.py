from datetime import date, timedelta

import pytest

from sorrisomais.exames_api import ClienteExames
from sorrisomais.api import ErroAcesso


class Falso:
    def __init__(self, data):
        self.data = data
        self.calls = []

    def _request(self, *args, **kwargs):
        self.calls.append((args, kwargs))
        return self.data


def test_get_exames_envia_filtros_e_nao_requer_rede():
    falso = Falso({"exames": [{"id": 1, "situacao": "Resultado disponível"}]})
    resultado = ClienteExames(falso).listar("token-ficticio", paciente_id=8, consulta_id=3)
    assert resultado[0]["id"] == 1
    assert falso.calls[0][0][:2] == ("GET", "/exames")
    assert falso.calls[0][1]["params"] == {"paciente_id": 8, "consulta_id": 3}


def test_post_exame_envia_somente_campos_textuais():
    falso = Falso({"exame": {"id": 2, "situacao": "Solicitado"}})
    ClienteExames(falso).solicitar("token-ficticio", paciente_id=8, consulta_id=3, tipo="Panorâmico", solicitado_em="2026-10-24")
    payload = falso.calls[0][1]["payload"]
    assert payload["tipo"] == "Panorâmico"
    assert "arquivo" not in payload and "url" not in payload


def test_post_exame_informa_paciente_ausente():
    with pytest.raises(ErroAcesso, match="Selecione um Paciente"):
        ClienteExames(Falso({})).solicitar(
            "token-ficticio", paciente_id=None, consulta_id=3,
            tipo="Panorâmico", solicitado_em="2026-10-24",
        )


def test_post_exame_rejeita_data_futura_antes_da_rede():
    with pytest.raises(ErroAcesso, match="não pode estar no futuro"):
        ClienteExames(Falso({})).solicitar(
            "token-ficticio", paciente_id=8, consulta_id=3,
            tipo="Panorâmico", solicitado_em=(date.today() + timedelta(days=1)).isoformat(),
        )


def test_post_exame_rejeita_observacao_acima_do_limite():
    with pytest.raises(ErroAcesso, match="no máximo 1000"):
        ClienteExames(Falso({})).solicitar(
            "token-ficticio", paciente_id=8, consulta_id=3,
            tipo="Panorâmico", solicitado_em="2026-10-24", observacoes="x" * 1001,
        )


def test_patch_exame_rejeita_situacao_desconhecida():
    with pytest.raises(ErroAcesso):
        ClienteExames(Falso({})).atualizar_situacao("token-ficticio", 2, situacao="Aberto")


def test_patch_exame_envia_resultado():
    falso = Falso({"exame": {"id": 2, "situacao": "Resultado disponível", "resultado": "Resultado fictício"}})
    ClienteExames(falso).atualizar_situacao("token-ficticio", 2, situacao="Resultado disponível", resultado="Resultado fictício")
    assert falso.calls[0][0][:2] == ("PATCH", "/exames/2/situacao")
    assert falso.calls[0][1]["payload"]["resultado"] == "Resultado fictício"
