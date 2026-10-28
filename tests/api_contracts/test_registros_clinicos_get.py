import pytest
from pathlib import Path

from conftest import resposta


def test_get_registros_clinicos_envia_filtro_e_conteudo_somente_no_endpoint_clinico(cliente, http):
    http.return_value = resposta({"registros_clinicos": [{
        "id": 5, "paciente_id": 4, "profissional_id": 8, "prontuario_id": 6,
        "conteudo": "Registro fictício", "liberado_paciente": False,
        "registrado_em": "2026-10-01T12:00:00Z",
    }]})
    resultado = cliente.listar_registros_clinicos("token-ficticio", paciente_id=4, consulta_id=9)
    assert resultado[0]["conteudo"] == "Registro fictício"
    assert resultado[0]["registrado_em"] == "2026-10-01T12:00:00Z"
    assert http.call_args.args[:2] == (
        "GET", "https://exemplo.invalid/api:teste/registros-clinicos",
    )
    assert http.call_args.kwargs["params"] == {"paciente_id": 4, "consulta_id": 9}


def test_get_registros_clinicos_do_portal_nao_envia_identificador_de_paciente(cliente, http):
    http.return_value = resposta({"registros_clinicos": [{
        "id": 7, "paciente_id": 4, "profissional_id": 8, "prontuario_id": 6,
        "conteudo": "Orientação fictícia liberada", "liberado_paciente": True,
        "registrado_em": "2026-10-01T12:00:00Z",
    }]})

    registros = cliente.listar_registros_clinicos("token-ficticio")

    assert registros[0]["liberado_paciente"] is True
    assert registros[0]["registrado_em"] == "2026-10-01T12:00:00Z"
    assert http.call_args.kwargs["params"] is None
    assert http.call_args.kwargs["headers"]["Authorization"] == "Bearer token-ficticio"


def test_get_registros_clinicos_limita_paciente_a_vinculo_proprio_e_itens_liberados():
    caminho = (Path(__file__).resolve().parents[2] / "backend" / "xano" / "api"
               / "sorriso_acesso" / "registros_clinicos_GET.xs")
    codigo = caminho.read_text(encoding="utf-8-sig")

    assert 'field_name = "conta_acesso_id"' in codigo
    assert "field_value = $auth.id" in codigo
    assert "var.update $paciente_escopo { value = $paciente_autenticado.id }" in codigo
    assert '$db.registro_clinico.liberado_paciente == true' in codigo
    assert '$solicitante.perfis|intersect:["profissional", "paciente"]' in codigo
    assert '"administrador"' not in codigo and '"recepcionista"' not in codigo
    assert 'auth = "conta_acesso"' in codigo

def test_export_get_filtra_no_xano_por_escopo_obrigatorio():
    raiz = Path(__file__).resolve().parents[2]
    export = (raiz / "backend/xano/api/sorriso_acesso/registros_clinicos_GET.xs").read_text(encoding="utf-8")

    assert 'auth = "conta_acesso"' in export
    assert "function.run sorriso_validar_sessao" in export
    assert '$db.registro_clinico.profissional_id == $profissional_escopo' in export
    assert '$db.registro_clinico.paciente_id == $paciente_escopo && $db.registro_clinico.liberado_paciente == true' in export
    assert '$registro.paciente_id != $input.paciente_id' in export
    assert '$registro.consulta_id != $input.consulta_id' in export
    assert 'history = false' in export
    where_clauses = [line.split("where =", 1)[1] for line in export.splitlines() if "where =" in line]
    assert len(where_clauses) == 3
    assert all("== null ||" not in clause for clause in where_clauses)
    assert where_clauses[2].strip() == "$db.registro_clinico_retificacao.registro_clinico_id == $registro.id"


def test_get_registros_clinicos_preserva_retificacoes_e_metadados(cliente, http):
    http.return_value = resposta({"registros_clinicos": [{
        "id": 5, "paciente_id": 4, "profissional_id": 8, "prontuario_id": 6,
        "conteudo": "Original fictício", "liberado_paciente": True,
        "registrado_em": "2026-10-01T12:00:00Z",
        "retificacoes": [{"id": 7, "profissional_id": 8,
                         "conteudo": "Correção fictícia", "justificativa": "Ajuste de digitação",
                         "criada_em": "2026-10-02T12:00:00Z"}],
    }]})
    registro = cliente.listar_registros_clinicos("token-ficticio")[0]
    assert registro["conteudo"] == "Original fictício"
    assert registro["retificacoes"] == [{
        "id": 7, "profissional_id": 8, "conteudo": "Correção fictícia",
        "justificativa": "Ajuste de digitação", "criada_em": "2026-10-02T12:00:00Z",
    }]


def test_get_xano_so_busca_retificacoes_para_paciente_quando_registro_esta_liberado():
    raiz = Path(__file__).resolve().parents[2]
    codigo = (raiz / "backend/xano/api/sorriso_acesso/registros_clinicos_GET.xs").read_text(encoding="utf-8")

    guarda = '($solicitante.perfis|intersect:["paciente"]|count) == 0 || $registro.liberado_paciente == true'
    assert guarda in codigo
    assert codigo.index(guarda) < codigo.index("db.query registro_clinico_retificacao")
    assert 'var $retificacoes { value = [] }' in codigo


def test_export_get_documenta_consulta_de_retificacoes_por_registro():
    raiz = Path(__file__).resolve().parents[2]
    codigo = (raiz / "backend/xano/api/sorriso_acesso/registros_clinicos_GET.xs").read_text(encoding="utf-8")

    inicio_loop = codigo.index("foreach ($registros_escopo)")
    fim_loop = codigo.index("\n      }\n    }\n  }\n  response", inicio_loop)
    bloco_loop = codigo[inicio_loop:fim_loop]

    # A consulta por ID mantém o vínculo autorizado sem depender de um operador
    # de lista cuja sintaxe Xano ainda não foi confirmada neste projeto.
    assert bloco_loop.count("db.query registro_clinico_retificacao") == 1
    assert "$db.registro_clinico_retificacao.registro_clinico_id == $registro.id" in bloco_loop
