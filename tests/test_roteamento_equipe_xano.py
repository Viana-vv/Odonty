"""Regressões do roteamento conectado com serviços totalmente simulados."""

from datetime import datetime, timedelta, timezone
from importlib.machinery import ModuleSpec
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from streamlit.testing.v1 import AppTest

from sorrisomais import navegacao, sessao
from sorrisomais.api import Credencial


def renderizar_equipe(conta, cliente):
    from sorrisomais import paginas_equipe

    paginas_equipe.renderizar(conta, cliente)


def cliente_teste():
    cliente = SimpleNamespace(
        configuracao=SimpleNamespace(
            modo_demonstracao=False,
            cadastro_paciente_habilitado=True,
        ),
        listar_opcoes_agenda=Mock(return_value={
            "pacientes": [{"id": 11, "nome": "Paciente Fictícia Aurora"}],
            "profissionais": [],
            "procedimentos": [],
        }),
        listar_consultas=Mock(return_value=[]),
    )
    return cliente


def conta_teste(perfil="recepcionista"):
    return SimpleNamespace(nome="Conta Fictícia", perfis=(perfil,))


def simular_modulos_integrados(monkeypatch, areas):
    import streamlit as st

    nomes = {f"sorrisomais.{navegacao.MODULOS_XANO[area]}": area for area in areas}
    modulos = {
        nome: SimpleNamespace(renderizar=lambda _cliente, _conta, area=area:
                              st.title(f"Tela {area}"))
        for nome, area in nomes.items()
    }
    monkeypatch.setattr(
        navegacao, "find_spec",
        lambda nome: ModuleSpec(nome, loader=None) if nome in nomes else None,
    )
    monkeypatch.setattr(navegacao, "import_module", lambda nome: modulos.get(nome))


def abrir_app(conta, cliente, pagina="inicio"):
    app = AppTest.from_function(renderizar_equipe, args=(conta, cliente))
    app.session_state["pagina_equipe"] = pagina
    app.session_state[sessao.CHAVE] = Credencial(
        "token-ficticio", datetime.now(timezone.utc) + timedelta(minutes=5)
    )
    return app.run()


def test_menu_conectado_abre_listagem_de_pacientes_sem_rede():
    cliente = cliente_teste()
    app = abrir_app(conta_teste(), cliente)

    assert not app.exception
    assert any(button.key == "menu-pacientes" and not button.disabled for button in app.button)
    app.button(key="menu-pacientes").click().run()

    assert any("Paciente Fictícia Aurora" in item.value for item in app.markdown)
    cliente.listar_opcoes_agenda.assert_called_once_with("token-ficticio")


def test_modulos_ausentes_ficam_desabilitados_no_menu(monkeypatch):
    monkeypatch.setattr(navegacao, "find_spec", lambda _nome: None)
    app = abrir_app(conta_teste("administrador"), cliente_teste())

    for area in ("profissionais", "procedimentos"):
        assert any(button.key == f"menu-indisponivel-{area}" and button.disabled
                   for button in app.button)


def test_rota_direta_para_area_sem_permissao_volta_a_visao_geral():
    app = abrir_app(conta_teste("recepcionista"), cliente_teste(), pagina="prontuarios")

    assert not app.exception
    assert app.session_state["pagina_equipe"] == "inicio"
    assert any("Aqui está um resumo" in item.value for item in app.caption)


def test_atalho_nova_consulta_na_visao_geral_depende_do_modulo_e_perfil(monkeypatch):
    cliente = cliente_teste()
    simular_modulos_integrados(monkeypatch, {"nova_consulta"})
    administrador = abrir_app(conta_teste("administrador"), cliente)
    assert not administrador.button(key="inicio-nova-consulta").disabled

    profissional = abrir_app(conta_teste("profissional"), cliente)
    assert not any(button.key == "inicio-nova-consulta" for button in profissional.button)

    administrador.button(key="inicio-nova-consulta").click().run()

    assert administrador.session_state["pagina_equipe"] == "nova_consulta"
    assert any(item.value == "Tela nova_consulta" for item in administrador.title)


def test_atalho_nova_consulta_fica_indisponivel_quando_modulo_esta_ausente(monkeypatch):
    monkeypatch.setattr(navegacao, "find_spec", lambda _nome: None)
    administrador = abrir_app(conta_teste("administrador"), cliente_teste())
    assert administrador.button(key="inicio-nova-consulta").disabled


@pytest.mark.parametrize(
    ("area", "perfil"),
    [
        ("profissionais", "administrador"),
        ("prontuarios", "profissional"),
        ("prontuarios", "paciente"),
        ("procedimentos", "administrador"),
        ("nova_consulta", "recepcionista"),
    ],
)
def test_modulos_isolados_abrem_com_perfil_autorizado(area, perfil, monkeypatch):
    simular_modulos_integrados(monkeypatch, {area})

    app = abrir_app(conta_teste(perfil), cliente_teste())
    chave_atalho = ("inicio-nova-consulta" if area == "nova_consulta"
                    else f"menu-{area}")
    assert any(button.key == chave_atalho and not button.disabled for button in app.button)
    if perfil == "paciente":
        assert app.session_state["pagina_equipe"] == "prontuarios"
        assert not any(button.key == "menu-inicio" for button in app.button)
        assert not any(button.key in {
            "menu-agenda", "menu-pacientes", "menu-profissionais",
            "menu-procedimentos", "menu-nova_consulta",
        } for button in app.button)
    app.button(key=chave_atalho).click().run()

    assert not app.exception
    assert any(item.value == f"Tela {area}" for item in app.title)


def test_modulo_disponivel_nao_abre_para_perfil_nao_autorizado(monkeypatch):
    simular_modulos_integrados(monkeypatch, {"procedimentos"})

    app = abrir_app(conta_teste("recepcionista"), cliente_teste(), pagina="procedimentos")

    assert not app.exception
    assert app.session_state["pagina_equipe"] == "inicio"
