"""Testes de interface da listagem conectada, sem chamadas de rede."""

from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from streamlit.testing.v1 import AppTest

from sorrisomais import pagina_pacientes_xano, sessao
from sorrisomais.api import Credencial, ErroAcesso


PACIENTES = [
    {"id": 11, "nome": "Paciente Fictícia Aurora"},
    {"id": 12, "nome": "Paciente Fictício Horizonte"},
]


def renderizar_tela(cliente, conta):
    from sorrisomais import pagina_pacientes_xano

    pagina_pacientes_xano.renderizar(cliente, conta)


@pytest.fixture
def cliente_pacientes():
    cliente = Mock()
    cliente.listar_opcoes_agenda.return_value = {
        "pacientes": [item.copy() for item in PACIENTES],
        "profissionais": [],
        "procedimentos": [],
    }
    return cliente


def abrir_tela(cliente):
    conta = SimpleNamespace(nome="Conta Fictícia", perfis=("recepcionista",))
    app = AppTest.from_function(renderizar_tela, args=(cliente, conta)).run()
    app.session_state[sessao.CHAVE] = Credencial(
        "token-ficticio",
        datetime.now(timezone.utc) + timedelta(minutes=5),
    )
    return app.run()


def test_lista_mostra_somente_id_e_nome(cliente_pacientes):
    app = abrir_tela(cliente_pacientes)

    assert not app.exception
    assert any(item.value == "Pacientes" for item in app.title)
    assert any("Paciente Fictícia Aurora" in item.value for item in app.markdown)
    assert any("Paciente Fictício Horizonte" in item.value for item in app.markdown)
    assert any(item.value == "11" for item in app.text)
    assert any(item.value == "12" for item in app.text)
    textos = [*app.markdown, *app.caption, *app.text, *app.title]
    assert not any("CPF" in item.value or "telefone" in item.value for item in textos)
    cliente_pacientes.listar_opcoes_agenda.assert_called_once_with("token-ficticio")


def test_lista_apresenta_hierarquia_visual_e_acao_de_cadastro(cliente_pacientes):
    app = abrir_tela(cliente_pacientes)

    assert not app.exception
    assert any(item.label == "Buscar Paciente" for item in app.text_input)
    assert any(item.key == "pacientes-xano-novo" for item in app.button)
    assert any(item.value == "ID" for item in app.caption)
    assert any(item.value == "Paciente" for item in app.caption)
    assert any(item.value == "Ações" for item in app.caption)
    cliente_pacientes.cadastrar_paciente.assert_not_called()


def test_acao_de_cadastro_nao_aparece_para_perfil_sem_permissao(cliente_pacientes):
    conta = SimpleNamespace(nome="Profissional Fictício", perfis=("profissional",))
    app = AppTest.from_function(renderizar_tela, args=(cliente_pacientes, conta)).run()
    app.session_state[sessao.CHAVE] = Credencial(
        "token-ficticio",
        datetime.now(timezone.utc) + timedelta(minutes=5),
    )
    app.run()

    assert not app.exception
    assert not any(item.key == "pacientes-xano-novo" for item in app.button)


def test_edicao_carrega_so_dados_cadastrais_e_nao_exibe_campo_clinico(cliente_pacientes):
    cliente_pacientes.obter_paciente.return_value = {
        "id": 11, "nome": "Paciente Fictícia Aurora", "data_nascimento": "2000-02-29",
        "cpf": "52998224725", "telefone": "11900000000", "celular": "11911112222",
        "email": "pessoa@example.com",
    }
    app = abrir_tela(cliente_pacientes)

    app.button(key="pacientes-xano-editar-11").click().run()

    assert not app.exception
    cliente_pacientes.obter_paciente.assert_called_once_with("token-ficticio", 11)
    assert app.text_input(key="pacientes_xano_edicao_nome").value == "Paciente Fictícia Aurora"
    assert app.text_input(key="pacientes_xano_edicao_email").value == "pessoa@example.com"
    rotulos = [item.label.casefold() for item in app.text_input]
    assert not any("observação" in rotulo or "saúde" in rotulo for rotulo in rotulos)


def test_falha_ao_carregar_edicao_nao_exibe_dados_pessoais(cliente_pacientes):
    cliente_pacientes.obter_paciente.side_effect = ErroAcesso(
        "Falha técnica com dado pessoal", 503,
    )
    app = abrir_tela(cliente_pacientes)

    app.button(key="pacientes-xano-editar-11").click().run()

    assert not app.exception
    assert any("Não foi possível concluir a edição" in item.value for item in app.error)
    assert not any("Falha técnica com dado pessoal" in item.value for item in app.error)
    assert not any(item.key.startswith("pacientes_xano_edicao_") for item in app.text_input)


def test_404_na_edicao_atualiza_lista_antes_de_exibir_falha(cliente_pacientes):
    paciente = {
        "id": 11, "nome": "Paciente Fictícia Aurora", "data_nascimento": "2000-02-29",
        "cpf": "52998224725", "telefone": "11900000000", "celular": "11911112222",
        "email": "pessoa@example.com",
    }
    cliente_pacientes.obter_paciente.side_effect = [
        ErroAcesso("não encontrado", 404), paciente,
    ]
    cliente_pacientes.listar_opcoes_agenda.side_effect = [
        {"pacientes": [item.copy() for item in PACIENTES], "profissionais": [], "procedimentos": []},
        {"pacientes": [item.copy() for item in PACIENTES], "profissionais": [], "procedimentos": []},
    ]
    app = abrir_tela(cliente_pacientes)

    app.button(key="pacientes-xano-editar-11").click().run()
    assert not app.exception
    app.button(key="pacientes-xano-editar-11").click().run()

    assert not app.exception
    assert cliente_pacientes.obter_paciente.call_count == 2
    assert app.text_input(key="pacientes_xano_edicao_nome").value == paciente["nome"]


def test_salvar_edicao_envia_campos_cadastrais_e_mostra_confirmacao(cliente_pacientes):
    cliente_pacientes.obter_paciente.return_value = {
        "id": 11, "nome": "Paciente Fictícia Aurora", "data_nascimento": "2000-02-29",
        "cpf": "52998224725", "telefone": "11900000000", "celular": "11911112222",
        "email": "pessoa@example.com",
    }
    cliente_pacientes.atualizar_paciente.return_value = None
    cliente_pacientes.listar_opcoes_agenda.side_effect = [
        {"pacientes": [item.copy() for item in PACIENTES], "profissionais": [], "procedimentos": []},
        {"pacientes": [{"id": 11, "nome": "Paciente Aurora Atualizada"}], "profissionais": [], "procedimentos": []},
    ]
    app = abrir_tela(cliente_pacientes)
    app.button(key="pacientes-xano-editar-11").click().run()
    app.text_input(key="pacientes_xano_edicao_nome").set_value("Paciente Aurora Atualizada")
    next(item for item in app.button if item.label.startswith("Salvar")).click().run()

    assert not app.exception
    cliente_pacientes.atualizar_paciente.assert_called_once_with(
        "token-ficticio", 11, nome="Paciente Aurora Atualizada",
        data_nascimento="2000-02-29", telefone="11900000000", cpf="52998224725",
        email="pessoa@example.com", celular="11911112222",
    )
    assert any("foram atualizados" in item.value for item in app.success)
    assert "pacientes_xano_edicao" not in app.session_state
    assert any("Paciente Aurora Atualizada" in item.value for item in app.markdown)


def test_falha_ao_salvar_preserva_formulario_com_mensagem_segura(cliente_pacientes):
    cliente_pacientes.obter_paciente.return_value = {
        "id": 11, "nome": "Paciente Fictícia Aurora", "data_nascimento": "2000-02-29",
        "cpf": "52998224725", "telefone": "11900000000", "celular": "11911112222",
        "email": "pessoa@example.com",
    }
    cliente_pacientes.atualizar_paciente.side_effect = ErroAcesso("DADO_PESSOAL", 409)
    app = abrir_tela(cliente_pacientes)
    app.button(key="pacientes-xano-editar-11").click().run()
    app.text_input(key="pacientes_xano_edicao_nome").set_value("Nome corrigido")
    next(item for item in app.button if item.label.startswith("Salvar")).click().run()

    assert not app.exception
    assert any("CPF informado já está cadastrado" in item.value for item in app.error)
    assert not any("DADO_PESSOAL" in item.value for item in app.error)
    assert app.text_input(key="pacientes_xano_edicao_nome").value == "Nome corrigido"
    assert "pacientes_xano_edicao" in app.session_state


def test_cancelar_edicao_descarta_dados_carregados(cliente_pacientes):
    cliente_pacientes.obter_paciente.return_value = {
        "id": 11, "nome": "Paciente Fictícia Aurora", "data_nascimento": "2000-02-29",
        "cpf": "52998224725", "telefone": "11900000000", "celular": "11911112222",
        "email": "pessoa@example.com",
    }
    app = abrir_tela(cliente_pacientes)
    app.button(key="pacientes-xano-editar-11").click().run()
    next(item for item in app.button if item.label == "Cancelar").click().run()

    assert not app.exception
    assert "pacientes_xano_edicao" not in app.session_state
    assert not any(item.key.startswith("pacientes_xano_edicao_") for item in app.text_input)


def test_busca_filtra_por_nome_sem_consultar_outros_campos(cliente_pacientes):
    app = abrir_tela(cliente_pacientes)
    app.text_input(key="pacientes-xano-busca").set_value("horizonte").run()

    assert any("Paciente Fictício Horizonte" in item.value for item in app.markdown)
    assert not any("Paciente Fictícia Aurora" in item.value for item in app.markdown)
    assert cliente_pacientes.listar_opcoes_agenda.call_count == 1


def test_atualizacao_manual_busca_novamente_na_api(cliente_pacientes):
    app = abrir_tela(cliente_pacientes)
    app.button(key="pacientes-xano-atualizar").click().run()

    assert cliente_pacientes.listar_opcoes_agenda.call_count == 2


def test_cache_expira_apos_vinte_segundos(cliente_pacientes, monkeypatch):
    tempo = [100.0]
    monkeypatch.setattr(pagina_pacientes_xano, "monotonic", lambda: tempo[0])
    app = abrir_tela(cliente_pacientes)

    tempo[0] += pagina_pacientes_xano.CACHE_TTL_SEGUNDOS + 1
    app.run()

    assert cliente_pacientes.listar_opcoes_agenda.call_count == 2


def test_troca_de_token_nao_reutiliza_cache_anterior(cliente_pacientes):
    app = abrir_tela(cliente_pacientes)
    app.session_state[sessao.CHAVE] = Credencial(
        "outro-token-ficticio",
        datetime.now(timezone.utc) + timedelta(minutes=5),
    )

    app.run()

    assert cliente_pacientes.listar_opcoes_agenda.call_count == 2
    assert cliente_pacientes.listar_opcoes_agenda.call_args.args == ("outro-token-ficticio",)


def test_lista_vazia_nao_insere_dados_demo(cliente_pacientes):
    cliente_pacientes.listar_opcoes_agenda.return_value["pacientes"] = []
    app = abrir_tela(cliente_pacientes)

    assert any("Nenhum Paciente disponível" in item.value for item in app.info)
    assert not any("Paciente Fictícia" in item.value or "Paciente Fictício" in item.value
                   for item in app.markdown)


def test_busca_sem_resultado_apresenta_estado_vazio(cliente_pacientes):
    app = abrir_tela(cliente_pacientes)
    app.text_input(key="pacientes-xano-busca").set_value("inexistente").run()

    assert any("Nenhum Paciente corresponde" in item.value for item in app.info)
    assert not any("Paciente Fictícia Aurora" in item.value for item in app.markdown)


def test_permissao_recusada_nao_exibe_cadastros(cliente_pacientes):
    cliente_pacientes.listar_opcoes_agenda.side_effect = ErroAcesso("erro técnico privado", 403)
    app = abrir_tela(cliente_pacientes)

    assert any("não tem permissão" in item.value for item in app.error)
    assert not any("erro técnico privado" in item.value for item in app.error)
    assert not any("Paciente Fictícia Aurora" in item.value for item in app.markdown)


def test_sessao_expirada_limpa_credencial_e_dados_cacheados(cliente_pacientes):
    cliente_pacientes.listar_opcoes_agenda.side_effect = ErroAcesso("credencial inválida", 401)
    app = abrir_tela(cliente_pacientes)

    assert any("Sua sessão expirou" in item.value for item in app.error)
    assert sessao.CHAVE not in app.session_state
    assert "pacientes_xano_cache" not in app.session_state


def test_falha_de_api_apresenta_mensagem_sem_dados(cliente_pacientes):
    cliente_pacientes.listar_opcoes_agenda.side_effect = ErroAcesso(
        "Não foi possível conectar ao serviço. Tente novamente em instantes.", 503
    )
    app = abrir_tela(cliente_pacientes)

    assert any("Não foi possível conectar ao serviço" in item.value for item in app.error)
    assert not any("Paciente Fictícia Aurora" in item.value for item in app.markdown)


def test_falha_nao_e_cacheada_e_pode_ser_tentada_novamente(cliente_pacientes):
    cliente_pacientes.listar_opcoes_agenda.side_effect = [
        ErroAcesso("Não foi possível conectar ao serviço. Tente novamente em instantes.", 503),
        {"pacientes": [item.copy() for item in PACIENTES],
         "profissionais": [], "procedimentos": []},
    ]
    app = abrir_tela(cliente_pacientes)
    assert any("Não foi possível conectar ao serviço" in item.value for item in app.error)

    app.button(key="pacientes-xano-atualizar").click().run()

    assert cliente_pacientes.listar_opcoes_agenda.call_count == 2
    assert any("Paciente Fictícia Aurora" in item.value for item in app.markdown)


def test_sessao_ausente_nao_chama_api(cliente_pacientes):
    conta = SimpleNamespace(nome="Conta Fictícia", perfis=("recepcionista",))
    app = AppTest.from_function(renderizar_tela, args=(cliente_pacientes, conta)).run()

    assert any("Sua sessão expirou" in item.value for item in app.info)
    cliente_pacientes.listar_opcoes_agenda.assert_not_called()
