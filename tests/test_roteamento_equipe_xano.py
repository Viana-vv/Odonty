"""Regressões do roteamento conectado com serviços totalmente simulados."""

from datetime import datetime, timedelta, timezone
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
    )
    return cliente


def conta_teste(perfil="recepcionista"):
    return SimpleNamespace(nome="Conta Fictícia", perfis=(perfil,))


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


def test_modulos_ausentes_ficam_desabilitados_no_menu():
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
    administrador = abrir_app(conta_teste("administrador"), cliente)
    atalho = administrador.button(key="inicio-nova-consulta")
    assert atalho.disabled

    profissional = abrir_app(conta_teste("profissional"), cliente)
    assert not any(button.key == "inicio-nova-consulta" for button in profissional.button)

    def abrir_modulo(area):
        assert area == "nova_consulta"
        import streamlit as st

        def renderizar(_cliente, _conta):
            st.title("Nova Consulta integrada")

        return SimpleNamespace(renderizar=renderizar)

    monkeypatch.setattr(navegacao, "modulo_xano_disponivel", lambda area: area == "nova_consulta")
    monkeypatch.setattr(navegacao, "carregar_modulo_xano", abrir_modulo)
    administrador = abrir_app(conta_teste("administrador"), cliente)
    administrador.button(key="inicio-nova-consulta").click().run()

    assert administrador.session_state["pagina_equipe"] == "nova_consulta"
    assert any(item.value == "Nova Consulta integrada" for item in administrador.title)


@pytest.mark.parametrize(
    ("area", "perfil"),
    [
        ("profissionais", "administrador"),
        ("prontuarios", "profissional"),
        ("procedimentos", "administrador"),
        ("nova_consulta", "recepcionista"),
    ],
)
def test_modulos_isolados_abrem_com_perfil_autorizado(area, perfil, monkeypatch):
    import streamlit as st

    chamadas = []

    def renderizar_modulo(_cliente, _conta):
        chamadas.append(area)
        st.title(f"Tela {area}")

    monkeypatch.setattr(navegacao, "modulo_xano_disponivel", lambda chave: chave == area)
    monkeypatch.setattr(
        navegacao,
        "carregar_modulo_xano",
        lambda chave: SimpleNamespace(renderizar=renderizar_modulo) if chave == area else None,
    )

    app = abrir_app(conta_teste(perfil), cliente_teste())
    chave_atalho = ("inicio-nova-consulta" if area == "nova_consulta"
                    else f"menu-{area}")
    assert any(button.key == chave_atalho and not button.disabled for button in app.button)
    app.button(key=chave_atalho).click().run()

    assert not app.exception
    assert chamadas == [area]
    assert any(item.value == f"Tela {area}" for item in app.title)


def test_modulo_disponivel_nao_abre_para_perfil_nao_autorizado(monkeypatch):
    monkeypatch.setattr(navegacao, "modulo_xano_disponivel", lambda area: area == "procedimentos")
    monkeypatch.setattr(
        navegacao, "carregar_modulo_xano",
        lambda _area: pytest.fail("O roteador não deve carregar módulo sem permissão"),
    )

    app = abrir_app(conta_teste("recepcionista"), cliente_teste(), pagina="procedimentos")

    assert not app.exception
    assert app.session_state["pagina_equipe"] == "inicio"
