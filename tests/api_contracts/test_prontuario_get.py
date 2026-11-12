"""Contratos do GET agregado de Prontuário sem chamadas reais ao Xano."""

from pathlib import Path
import pytest

from conftest import resposta
from sorrisomais.contratos_clinicos import DadosContratoInvalidos


SECOES = (
    "anamnese",
    "historico_odontologico",
    "odontograma",
    "exame_clinico",
    "diagnosticos",
    "plano_tratamento",
    "procedimentos",
    "exames",
    "prescricoes",
    "evolucoes",
    "documentos",
)


def agregado(**sobrescritas):
    resultado = {
        "paciente": {
            "id": 12,
            "nome": "Paciente Fictícia Aurora",
            "cpf": "00000000000",
            "data_nascimento": "1990-01-01",
            "telefone": "(11) 90000-0000",
            "endereco": "Rua Fictícia, 10",
        },
        "prontuario": {"id": 30, "paciente_id": 12, "situacao": "ativo"},
        **{secao: [] for secao in SECOES},
    }
    resultado.update(sobrescritas)
    return {"prontuario": resultado}


def test_get_prontuario_agregado_envia_paciente_e_retorna_todas_as_secoes(cliente, http):
    http.return_value = resposta(agregado(
        anamnese=[{"versao": 2, "alergias": "Nenhuma fictícia"}],
        odontograma=[{"numero_dente": "11", "condicao": "saudável"}],
        diagnosticos=[{"descricao": "Diagnóstico fictício"}],
        plano_tratamento=[{"objetivo": "Plano fictício"}],
        procedimentos=[{"situacao": "realizado"}],
        exames=[{"tipo": "Radiografia fictícia", "situacao": "Solicitado"}],
        prescricoes=[{"medicamento": "Medicamento fictício"}],
        evolucoes=[{"conteudo": "Evolução fictícia"}],
        documentos=[{"tipo": "Atestado fictício", "referencia_privada": "ref-ficticia"}],
    ))

    resultado = cliente.obter_prontuario("token-ficticio", 12)

    assert resultado["paciente"]["nome"] == "Paciente Fictícia Aurora"
    assert resultado["paciente"]["endereco"] == "Rua Fictícia, 10"
    assert all(secao in resultado for secao in SECOES)
    assert resultado["documentos"][0]["referencia_privada"] == "ref-ficticia"
    assert http.call_args.args[:2] == (
        "GET", "https://exemplo.invalid/api:teste/prontuarios/12",
    )
    assert http.call_args.kwargs["headers"]["Authorization"] == "Bearer token-ficticio"


def test_get_prontuario_preserva_estados_vazios_sem_inventar_conteudo(cliente, http):
    http.return_value = resposta(agregado())

    resultado = cliente.obter_prontuario("token-ficticio", 12)

    assert all(resultado[secao] == [] for secao in SECOES)
    assert resultado["paciente"]["endereco"] == "Rua Fictícia, 10"


def test_get_prontuario_rejeita_identificador_invalido_sem_rede(cliente, http):
    with pytest.raises(DadosContratoInvalidos):
        cliente.obter_prontuario("token-ficticio", 0)

    http.assert_not_called()


def test_get_prontuario_rejeita_resposta_sem_agregado(cliente, http):
    http.return_value = resposta({"prontuario": {"paciente": {"id": 12}}})

    with pytest.raises(DadosContratoInvalidos):
        cliente.obter_prontuario("token-ficticio", 12)


def test_get_prontuario_documenta_autenticacao_escopo_e_perfis_no_xano():
    caminho = (Path(__file__).resolve().parents[2] / "backend" / "xano" / "api"
               / "sorriso_acesso" / "prontuario_GET.xs")
    codigo = caminho.read_text(encoding="utf-8-sig")

    assert 'auth = "conta_acesso"' in codigo
    assert "function.run sorriso_validar_sessao" in codigo
    assert '"administrador"' not in codigo or "conteudo_clinico" not in codigo
    assert '"recepcionista"' not in codigo or "conteudo_clinico" not in codigo
    assert "$input.paciente_id" in codigo
    assert "liberado_paciente" in codigo
    assert "history = false" in codigo


def test_get_prontuario_nao_expoe_url_publica_nem_conteudo_de_outro_paciente():
    caminho = (Path(__file__).resolve().parents[2] / "backend" / "xano" / "api"
               / "sorriso_acesso" / "prontuario_GET.xs")
    codigo = caminho.read_text(encoding="utf-8-sig")

    assert "url_publica" not in codigo
    assert "url_publica_permanente" not in codigo
    assert "paciente_id" in codigo
    assert "profissional_id" in codigo
