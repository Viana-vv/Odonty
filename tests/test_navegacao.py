from sorrisomais.navegacao import (
    MODULOS_XANO,
    areas_visiveis,
    modulo_xano_disponivel,
    pode_acessar,
)


def test_menu_demonstrativo_mostra_areas_autorizadas_por_perfil():
    areas = areas_visiveis({"recepcionista"}, modo_demonstracao=True)
    assert {area["chave"] for area in areas} == {
        "inicio", "agenda", "pacientes", "profissionais",
    }
    assert all(area["disponivel"] for area in areas)


def test_dentista_recebe_prontuario_mas_nao_areas_administrativas():
    areas = areas_visiveis({"profissional"}, modo_demonstracao=True)
    assert {area["chave"] for area in areas} == {"inicio", "agenda", "prontuarios"}
    assert pode_acessar({"profissional"}, "prontuarios")
    assert not pode_acessar({"profissional"}, "procedimentos")


def test_modo_xano_habilita_pacientes_e_agenda_com_modulos_integrados():
    areas = {item["chave"]: item["disponivel"]
             for item in areas_visiveis({"recepcionista"}, modo_demonstracao=False)}
    assert areas["inicio"]
    assert areas["pacientes"]
    assert not areas["profissionais"]
    assert areas["agenda"]
    assert "prontuarios" not in areas


def test_modulos_ausentes_permanecem_indisponiveis_no_modo_xano():
    areas = {item["chave"]: item["disponivel"]
             for item in areas_visiveis({"recepcionista"}, modo_demonstracao=False)}

    assert not areas["profissionais"]
    assert not areas.get("prontuarios", False)
    assert not areas.get("procedimentos", False)
    assert not modulo_xano_disponivel("nova_consulta")
    assert set(MODULOS_XANO) == {
        "pacientes", "profissionais", "prontuarios", "procedimentos", "nova_consulta",
    }
    assert MODULOS_XANO["prontuarios"] == "pagina_prontuario_xano"


def test_nova_consulta_restrita_a_administrador_e_recepcionista():
    assert pode_acessar({"administrador"}, "nova_consulta")
    assert pode_acessar({"recepcionista"}, "nova_consulta")
    assert not pode_acessar({"profissional"}, "nova_consulta")
    assert pode_acessar({"profissional"}, "prontuarios")
    assert not pode_acessar({"administrador"}, "prontuarios")


def test_desligar_cadastro_remove_entrada_de_paciente():
    areas = areas_visiveis({"recepcionista"}, modo_demonstracao=True,
                           cadastro_paciente_habilitado=False)
    assert "pacientes" not in {item["chave"] for item in areas}
