from sorrisomais.navegacao import areas_visiveis, pode_acessar


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


def test_modo_xano_habilita_agenda_ja_integrada():
    areas = {item["chave"]: item["disponivel"]
             for item in areas_visiveis({"recepcionista"}, modo_demonstracao=False)}
    assert areas["inicio"]
    assert not areas["pacientes"]
    assert not areas["profissionais"]
    assert areas["agenda"]
    assert "prontuarios" not in areas


def test_desligar_cadastro_remove_entrada_de_paciente():
    areas = areas_visiveis({"recepcionista"}, modo_demonstracao=True,
                           cadastro_paciente_habilitado=False)
    assert "pacientes" not in {item["chave"] for item in areas}
