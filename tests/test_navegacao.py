from sorrisomais.navegacao import (
    MODULOS_XANO,
    areas_visiveis,
    modulo_xano_disponivel,
    pode_acessar,
)


def test_menu_demonstrativo_mostra_areas_autorizadas_por_perfil():
    areas = areas_visiveis({"recepcionista"}, modo_demonstracao=True)
    assert {area["chave"] for area in areas} == {
        "inicio", "agenda", "pacientes", "profissionais", "reagendar_consulta",
    }
    assert all(area["disponivel"] for area in areas)


def test_dentista_recebe_prontuario_mas_nao_areas_administrativas():
    areas = areas_visiveis({"profissional"}, modo_demonstracao=True)
    assert {area["chave"] for area in areas} == {
        "inicio", "agenda", "prontuarios", "exames",
    }
    assert pode_acessar({"profissional"}, "prontuarios")
    assert not pode_acessar({"profissional"}, "procedimentos")


def test_paciente_recebe_somente_prontuario_no_modo_xano(monkeypatch):
    from importlib.machinery import ModuleSpec
    from sorrisomais import navegacao

    nome_modulo = f"sorrisomais.{MODULOS_XANO['prontuarios']}"
    monkeypatch.setattr(
        navegacao, "find_spec",
        lambda nome: ModuleSpec(nome, loader=None) if nome == nome_modulo else None,
    )

    areas = areas_visiveis({"paciente"}, modo_demonstracao=False)

    assert {area["chave"] for area in areas} == {"prontuarios"}
    assert all(area["disponivel"] for area in areas)
    assert pode_acessar({"paciente"}, "prontuarios")
    assert not pode_acessar({"paciente"}, "pacientes")
    assert not pode_acessar({"paciente"}, "agenda")
    assert not pode_acessar({"paciente"}, "profissionais")
    assert not pode_acessar({"paciente"}, "procedimentos")


def test_modo_xano_habilita_areas_com_modulos_integrados(monkeypatch):
    from importlib.machinery import ModuleSpec
    from sorrisomais import navegacao

    integrados = {f"sorrisomais.{nome}" for nome in MODULOS_XANO.values()}
    monkeypatch.setattr(
        navegacao, "find_spec",
        lambda nome: ModuleSpec(nome, loader=None) if nome in integrados else None,
    )
    areas = {item["chave"]: item["disponivel"]
             for item in areas_visiveis({"administrador"}, modo_demonstracao=False)}
    assert areas["inicio"]
    assert areas["pacientes"]
    assert areas["profissionais"]
    assert areas["procedimentos"]
    assert modulo_xano_disponivel("nova_consulta")
    assert areas["agenda"]
    assert "prontuarios" not in areas


def test_modo_xano_habilita_prontuario_para_profissional_com_modulo_integrado(monkeypatch):
    from importlib.machinery import ModuleSpec
    from sorrisomais import navegacao

    nome_modulo = f"sorrisomais.{MODULOS_XANO['prontuarios']}"
    monkeypatch.setattr(
        navegacao, "find_spec",
        lambda nome: ModuleSpec(nome, loader=None) if nome == nome_modulo else None,
    )

    areas = {item["chave"]: item["disponivel"]
             for item in areas_visiveis({"profissional"}, modo_demonstracao=False)}

    assert areas["prontuarios"]


def test_modulos_ausentes_permanecem_indisponiveis_no_modo_xano(monkeypatch):
    from sorrisomais import navegacao

    monkeypatch.setattr(navegacao, "find_spec", lambda _nome: None)
    areas = {item["chave"]: item["disponivel"]
             for item in areas_visiveis({"recepcionista"}, modo_demonstracao=False)}

    assert not areas["profissionais"]
    assert not areas.get("prontuarios", False)
    assert not areas.get("procedimentos", False)
    assert not areas["reagendar_consulta"]
    assert not modulo_xano_disponivel("nova_consulta")
    assert not modulo_xano_disponivel("exames")
    assert not modulo_xano_disponivel("reagendar_consulta")
    assert not modulo_xano_disponivel("procedimentos_consulta")
    assert set(MODULOS_XANO) == {
        "pacientes", "profissionais", "prontuarios", "procedimentos", "exames",
        "reagendar_consulta", "procedimentos_consulta", "nova_consulta",
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
