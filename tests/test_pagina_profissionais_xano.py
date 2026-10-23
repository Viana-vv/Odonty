"""Testes de interface e autorização sem requisições de rede."""

from contextlib import nullcontext
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from sorrisomais.api import ContaAcesso, Credencial, ErroAcesso
from sorrisomais import pagina_profissionais_xano as pagina


PROFISSIONAIS = [
    {"id": 201, "nome": "Dra. Exemplo Sorriso", "cro": "SP-123",
     "especialidade": {"id": 3, "nome": "Ortodontia"}, "email": None,
     "telefone": "11999990000", "situacao": "ativo"},
    {"id": 202, "nome": "Dr. Nome Fictício", "cro": "RJ-456",
     "especialidade": {"id": 4, "nome": "Clínica geral"}, "email": "dr@exemplo.invalid",
     "telefone": None, "situacao": "inativo"},
]


class InterfaceFalsa:
    def __init__(self):
        self.session_state = {"credencial": Credencial(
            "token-ficticio", datetime.now(timezone.utc) + timedelta(hours=1))}
        self.textos, self.infos, self.erros = [], [], []
        self.colunas_criadas, self.botoes = [], []
        self.cliques = {}
        self.confirmacoes = {}

    def button(self, texto, **kwargs):
        self.botoes.append((texto, kwargs))
        return self.cliques.pop(kwargs.get("key"), False)

    def checkbox(self, texto, key=None, **_kwargs):
        self.textos.append(texto)
        return self.confirmacoes.get(key, False)

    def title(self, texto): self.textos.append(texto)
    def write(self, texto): self.textos.append(texto)
    def info(self, texto): self.infos.append(texto)
    def error(self, texto): self.erros.append(texto)
    def success(self, texto): self.textos.append(texto)
    def caption(self, texto): self.textos.append(texto)
    def subheader(self, texto): self.textos.append(texto)
    def markdown(self, texto, **_kwargs): self.textos.append(texto)
    def spinner(self, _texto): return nullcontext()
    def rerun(self): return None
    def __enter__(self): return self
    def __exit__(self, *_args): return False
    def container(self, **_kwargs): return nullcontext()

    def columns(self, quantidade, **_kwargs):
        self.colunas_criadas.append(quantidade)
        total = quantidade if isinstance(quantidade, int) else len(quantidade)
        return [self] * total


@pytest.fixture
def tela(monkeypatch):
    interface = InterfaceFalsa()
    monkeypatch.setattr(pagina, "st", interface)
    cliente = Mock()
    cliente.listar_profissionais.return_value = PROFISSIONAIS
    expira = datetime.now(timezone.utc) + timedelta(hours=1)
    conta = ContaAcesso(1, "Conta Fictícia", ("administrador",), expira)
    return interface, cliente, conta


def test_cartoes_exibem_dados_do_contrato_e_situacao(tela):
    interface, cliente, conta = tela
    pagina.renderizar(cliente, conta)
    for dado in ("Dra. Exemplo Sorriso", "SP-123", "Ortodontia", "Não informado",
                 "11999990000", "Inativo", "Ativo"):
        assert any(dado in texto for texto in interface.textos), repr(interface.textos)
    assert cliente.listar_profissionais.call_count == 1
    assert interface.colunas_criadas == [3, [1, 2], [1, 2]]


def test_recepcionista_consulta_sem_controles_de_alteracao(tela):
    interface, cliente, _ = tela
    pagina.renderizar(cliente, SimpleNamespace(perfis=("recepcionista",)))
    assert cliente.listar_profissionais.call_count == 1
    assert not any("Confirmar " in texto for texto, _ in interface.botoes)


def test_perfil_nao_autorizado_nao_consulta(tela):
    interface, cliente, _ = tela
    pagina.renderizar(cliente, SimpleNamespace(perfis=("profissional",)))
    assert cliente.listar_profissionais.call_count == 0
    assert interface.infos


def test_lista_vazia_e_erro_de_api(tela):
    interface, cliente, conta = tela
    cliente.listar_profissionais.return_value = []
    pagina.renderizar(cliente, conta)
    assert interface.infos == ["Não há Profissionais cadastrados para exibir."]
    interface.cliques["profissionais-xano-atualizar"] = True
    cliente.listar_profissionais.side_effect = ErroAcesso("Serviço indisponível.", 503)
    pagina.renderizar(cliente, conta)
    assert interface.erros == ["Serviço indisponível."]


def test_sessao_expirada_limpa_credencial(tela):
    interface, cliente, conta = tela
    cliente.listar_profissionais.side_effect = ErroAcesso("Sessão expirada.", 401)
    pagina.renderizar(cliente, conta)
    assert "credencial" not in interface.session_state


def test_sem_sessao_nao_consulta(tela):
    interface, cliente, conta = tela
    interface.session_state.clear()
    pagina.renderizar(cliente, conta)
    cliente.listar_profissionais.assert_not_called()


def test_admin_altera_situacao_somente_apos_confirmacao(tela):
    interface, cliente, conta = tela
    cliente.listar_profissionais.side_effect = [PROFISSIONAIS, [
        {**PROFISSIONAIS[0], "situacao": "inativo"}, PROFISSIONAIS[1],
    ]]
    interface.confirmacoes["profissional-confirmar-201"] = True
    interface.cliques["profissional-situacao-201"] = True
    pagina.renderizar(cliente, conta)
    cliente.atualizar_situacao_profissional.assert_called_once_with("token-ficticio", 201, "inativo")
    assert cliente.listar_profissionais.call_count == 2
    assert any("Situação" in texto for texto in interface.textos)


def test_admin_nao_altera_sem_confirmacao(tela):
    interface, cliente, conta = tela
    pagina.renderizar(cliente, conta)
    cliente.atualizar_situacao_profissional.assert_not_called()


def test_layout_usa_grade_de_cartoes(tela):
    interface, cliente, conta = tela
    pagina.renderizar(cliente, conta)
    assert interface.colunas_criadas[0] == 3


def test_cache_reutiliza_lista_na_mesma_sessao(tela, monkeypatch):
    interface, cliente, conta = tela
    monkeypatch.setattr(pagina.time, "monotonic", lambda: 100.0)
    pagina.renderizar(cliente, conta)
    pagina.renderizar(cliente, conta)
    cliente.listar_profissionais.assert_called_once_with("token-ficticio")


def test_cache_expira_e_troca_de_token_invalida_lista(tela, monkeypatch):
    interface, cliente, conta = tela
    agora = [100.0]
    monkeypatch.setattr(pagina.time, "monotonic", lambda: agora[0])
    pagina.renderizar(cliente, conta)
    agora[0] = 120.0
    pagina.renderizar(cliente, conta)
    interface.session_state["credencial"] = Credencial(
        "outro-token", datetime.now(timezone.utc) + timedelta(hours=1))
    pagina.renderizar(cliente, conta)
    assert cliente.listar_profissionais.call_count == 3


def test_atualizacao_manual_forca_consulta(tela):
    interface, cliente, conta = tela
    pagina.renderizar(cliente, conta)
    interface.cliques["profissionais-xano-atualizar"] = True
    pagina.renderizar(cliente, conta)
    assert cliente.listar_profissionais.call_count == 2


def test_falha_na_atualizacao_nao_preserva_cache_antigo(tela):
    interface, cliente, conta = tela
    pagina.renderizar(cliente, conta)
    interface.textos.clear()
    interface.cliques["profissionais-xano-atualizar"] = True
    cliente.listar_profissionais.side_effect = ErroAcesso("Falha fictícia.", 503)
    pagina.renderizar(cliente, conta)
    assert pagina._CHAVE_CACHE_PROFISSIONAIS not in interface.session_state
    assert "Dra. Exemplo Sorriso" not in interface.textos


def test_erro_ao_alterar_situacao_preserva_situacao_confirmada(tela):
    interface, cliente, conta = tela
    interface.confirmacoes["profissional-confirmar-201"] = True
    interface.cliques["profissional-situacao-201"] = True
    cliente.atualizar_situacao_profissional.side_effect = ErroAcesso("Sem permissão.", 403)
    pagina.renderizar(cliente, conta)
    assert interface.erros == ["Sem permissão."]
    assert "Ativo" in interface.textos
