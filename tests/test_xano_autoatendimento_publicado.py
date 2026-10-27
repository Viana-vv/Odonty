from __future__ import annotations

import os

import pytest
import requests


HABILITADO = os.getenv("XANO_TESTAR_AUTOATENDIMENTO_PUBLICADO") == "1"
BASE_URL = os.getenv("XANO_API_BASE_URL", "").strip().rstrip("/")
EMAIL = os.getenv("XANO_AUTOATENDIMENTO_EMAIL", "").strip()
SENHA = os.getenv("XANO_AUTOATENDIMENTO_SENHA", "")


@pytest.mark.skipif(not HABILITADO, reason="defina XANO_TESTAR_AUTOATENDIMENTO_PUBLICADO=1")
def test_autoatendimento_publicado_read_only():
    """Verifica os contratos publicados sem criar ou alterar dados clínicos."""
    ausentes = [nome for nome, valor in (
        ("XANO_API_BASE_URL", BASE_URL),
        ("XANO_AUTOATENDIMENTO_EMAIL", EMAIL),
        ("XANO_AUTOATENDIMENTO_SENHA", SENHA),
    ) if not valor]
    if ausentes:
        pytest.fail("Pré-requisitos ausentes: " + ", ".join(ausentes))
    if not BASE_URL.startswith("https://"):
        pytest.fail("XANO_API_BASE_URL precisa usar HTTPS.")

    sessao = requests.Session()
    sessao.headers.update({"Accept": "application/json"})
    token = None
    try:
        for rota in ("/auth/me", "/consultas", "/registros-clinicos", "/exames"):
            sem_sessao = sessao.get(f"{BASE_URL}{rota}", timeout=15, allow_redirects=False)
            assert sem_sessao.status_code == 401, f"GET {rota} deve rejeitar sessão ausente."

        resposta = sessao.post(
            f"{BASE_URL}/auth/login", json={"email": EMAIL, "senha": SENHA},
            timeout=15, allow_redirects=False,
        )
        assert resposta.status_code == 200, "O login da Conta de Acesso fictícia falhou."
        corpo = resposta.json()
        token = corpo.get("token")
        assert isinstance(token, str) and token and not any(c.isspace() for c in token)
        assert corpo.get("tipo_token") == "Bearer"
        sessao.headers["Authorization"] = f"Bearer {token}"

        identidade = sessao.get(f"{BASE_URL}/auth/me", timeout=15, allow_redirects=False)
        assert identidade.status_code == 200, "A identidade da Conta de Acesso não foi confirmada."
        conta = identidade.json().get("conta", {})
        assert "paciente" in conta.get("perfis", [])
        assert conta.get("situacao") == "ativo", "A Conta de Acesso não está ativa."

        for rota, chave in (("consultas", "consultas"),
                            ("registros-clinicos", "registros_clinicos"),
                            ("exames", "exames")):
            leitura = sessao.get(f"{BASE_URL}/{rota}", timeout=15, allow_redirects=False)
            assert leitura.status_code == 200, f"GET /{rota} não foi autorizado."
            itens = leitura.json().get(chave)
            assert isinstance(itens, list)
            # Não há parâmetro paciente_id: o Xano deriva o escopo da sessão.
            assert "paciente_id" not in leitura.request.url
            if rota == "registros-clinicos":
                assert all(item.get("liberado_paciente") is True for item in itens), "GET /registros-clinicos retornou Registro Clínico não liberado."
            if rota == "exames":
                assert all(
                    item.get("situacao") == "Resultado disponível" or not item.get("resultado")
                    for item in itens
                )
                assert all(not item.get("arquivo_url") for item in itens)

    finally:
        if token:
            sessao.headers["Authorization"] = f"Bearer {token}"
            try:
                logout = sessao.post(f"{BASE_URL}/auth/logout", timeout=15, allow_redirects=False)
                assert logout.status_code in (204, 401)
            finally:
                token = None
                sessao.headers.pop("Authorization", None)
        sessao.close()



