"""Cliente explícito dos contratos de redefinição; nunca repete requisições."""

import base64
import re
from datetime import datetime, timedelta

import requests

from .api import ErroAcesso
from .uuid7 import validar_uuid7


class ErroRedefinicaoSenha(ErroAcesso):
    def __init__(self, mensagem="Não foi possível confirmar o resultado da operação.",
                 status=None, codigo=None, *, retry_after=None, resultado_incerto=False):
        super().__init__(mensagem, status, codigo)
        self.retry_after = retry_after
        self.resultado_incerto = resultado_incerto


ERROS_SOLICITACAO = {
    400: {"DADOS_INVALIDOS"}, 401: {"SESSAO_INVALIDA"}, 403: {"ACESSO_NEGADO"},
    404: {"CONTA_NAO_ENCONTRADA"},
    409: {"CONTA_INELEGIVEL", "OPERACAO_CONFLITANTE", "OPERACAO_ANTIGA", "OPERACAO_FUTURA"},
    429: {"LIMITE_ENVIO"}, 503: {"RECURSO_INDISPONIVEL"},
}
ERROS_CONSULTA = {
    400: {"DADOS_INVALIDOS"}, 401: {"SESSAO_INVALIDA"}, 403: {"ACESSO_NEGADO"},
    404: {"OPERACAO_NAO_ENCONTRADA"}, 503: {"SERVICO_INDISPONIVEL"},
}
ERROS_CONFIRMACAO = {
    400: {"DADOS_INVALIDOS", "LINK_INDISPONIVEL"},
    409: {"ENVIO_EM_PROCESSAMENTO"}, 429: {"LIMITE_CONFIRMACAO"},
    503: {"SERVICO_INDISPONIVEL"},
}
MENSAGENS = {
    400: "Confira os dados informados ou solicite outro link à clínica.",
    401: "Sua sessão não é válida. Entre novamente.",
    403: "Sua conta não tem permissão para esta operação.",
    404: "O resultado solicitado não está disponível.",
    409: "A operação não pode ser concluída agora. Confira o resultado antes de tentar novamente.",
    429: "Aguarde antes de tentar novamente.",
    503: "O serviço está temporariamente indisponível.",
}


def validar_codigo(codigo):
    """Valida a representação canônica de 32 bytes, sem normalização."""
    if not isinstance(codigo, str) or not re.fullmatch(r"[A-Za-z0-9_-]{43}", codigo):
        raise ErroRedefinicaoSenha(MENSAGENS[400], 400, "LINK_INDISPONIVEL")
    bruto = base64.urlsafe_b64decode(codigo + "=")
    if len(bruto) != 32 or base64.urlsafe_b64encode(bruto).decode().rstrip("=") != codigo:
        raise ErroRedefinicaoSenha(MENSAGENS[400], 400, "LINK_INDISPONIVEL")
    return codigo


class ClienteRedefinicaoSenha:
    def __init__(self, configuracao, transporte=None):
        self.configuracao = configuracao
        self._transporte = transporte

    @staticmethod
    def _entrada_administrativa(token, conta_id, operacao_id):
        if not isinstance(token, str) or not token or any(c.isspace() for c in token):
            raise ErroRedefinicaoSenha(MENSAGENS[401], 401, "SESSAO_INVALIDA")
        if type(conta_id) is not int or conta_id <= 0:
            raise ErroRedefinicaoSenha(MENSAGENS[400], 400, "DADOS_INVALIDOS")
        try:
            validar_uuid7(operacao_id)
        except (ValueError, TypeError, AttributeError):
            raise ErroRedefinicaoSenha(MENSAGENS[400], 400, "DADOS_INVALIDOS") from None

    def _requisitar(self, metodo, rota, erros, *, token=None, payload=None, sucesso=200):
        headers = {"Accept": "application/json", "Cache-Control": "no-store"}
        if token is not None:
            headers["Authorization"] = "Bearer " + token
        try:
            resposta = (self._transporte or requests.request)(
                metodo, self.configuracao.api_base_url + rota, json=payload,
                headers=headers, timeout=self.configuracao.timeout, allow_redirects=False,
            )
            with resposta:
                status = resposta.status_code
                if status == sucesso == 204:
                    # O contrato público não contém corpo nem credencial de sessão.
                    if getattr(resposta, "content", b"") != b"":
                        raise ErroRedefinicaoSenha(resultado_incerto=True)
                    return None
                try:
                    dados = resposta.json()
                except ValueError:
                    raise ErroRedefinicaoSenha(resultado_incerto=metodo == "POST") from None
                if status == sucesso:
                    return dados
                codigo = dados.get("codigo") if isinstance(dados, dict) else None
                if (not isinstance(codigo, str) or codigo not in erros.get(status, set())
                        or set(dados) != {"codigo", "mensagem"}
                        or not isinstance(dados["mensagem"], str)):
                    raise ErroRedefinicaoSenha(resultado_incerto=metodo == "POST")
                retry_after = None
                if status == 429 or codigo == "ENVIO_EM_PROCESSAMENTO":
                    espera = resposta.headers.get("Retry-After")
                    if isinstance(espera, str) and re.fullmatch(r"[0-9]+", espera) and int(espera) > 0:
                        retry_after = int(espera)
                    elif codigo == "ENVIO_EM_PROCESSAMENTO":
                        raise ErroRedefinicaoSenha(resultado_incerto=True)
                raise ErroRedefinicaoSenha(MENSAGENS[status], status, codigo, retry_after=retry_after)
        except requests.RequestException:
            raise ErroRedefinicaoSenha(resultado_incerto=metodo == "POST") from None

    @staticmethod
    def _projecao(dados, operacao_id, *, incerto=False):
        campos = {"operacao_id", "criada_em", "consultavel_ate", "estado_envio",
                  "estado_link", "expira_em", "envio_limite_em"}
        try:
            if not isinstance(dados, dict) or set(dados) != campos or dados["operacao_id"] != operacao_id:
                raise ValueError
            validar_uuid7(dados["operacao_id"])
            if dados["estado_envio"] not in {"processando", "aceito", "falhou", "desconhecido"}:
                raise ValueError
            if dados["estado_link"] not in {"pendente", "ativo", "consumido", "expirado", "substituido", "invalidado"}:
                raise ValueError
            if (dados["estado_link"] == "pendente" and dados["estado_envio"] != "processando"
                    or dados["estado_link"] == "ativo" and dados["estado_envio"] not in {"aceito", "desconhecido"}):
                raise ValueError
            datas = {}
            for campo in ("criada_em", "consultavel_ate", "expira_em", "envio_limite_em"):
                valor = dados[campo]
                if not isinstance(valor, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z", valor):
                    raise ValueError
                datas[campo] = datetime.fromisoformat(valor.replace("Z", "+00:00"))
            if (datas["consultavel_ate"] != datas["criada_em"] + timedelta(days=30)
                    or datas["expira_em"] != datas["criada_em"] + timedelta(minutes=15)
                    or not datas["criada_em"] < datas["envio_limite_em"] <= datas["criada_em"] + timedelta(seconds=30)):
                raise ValueError
        except (ValueError, TypeError, KeyError, AttributeError, OverflowError):
            raise ErroRedefinicaoSenha(resultado_incerto=incerto) from None
        return dict(dados)

    def solicitar(self, token, conta_id, operacao_id):
        self._entrada_administrativa(token, conta_id, operacao_id)
        dados = self._requisitar("POST", f"/contas-acesso/{conta_id}/redefinicoes-senha",
                                ERROS_SOLICITACAO, token=token, payload={"operacao_id": operacao_id})
        return self._projecao(dados, operacao_id, incerto=True)

    def consultar(self, token, conta_id, operacao_id):
        self._entrada_administrativa(token, conta_id, operacao_id)
        dados = self._requisitar("GET", f"/contas-acesso/{conta_id}/redefinicoes-senha/{operacao_id}",
                                ERROS_CONSULTA, token=token)
        return self._projecao(dados, operacao_id)

    def confirmar(self, codigo, senha):
        validar_codigo(codigo)
        if not isinstance(senha, str) or not 12 <= len(senha) <= 128:
            raise ErroRedefinicaoSenha(MENSAGENS[400], 400, "DADOS_INVALIDOS")
        return self._requisitar("POST", "/auth/redefinicoes-senha/confirmar", ERROS_CONFIRMACAO,
                                payload={"codigo": codigo, "senha": senha}, sucesso=204)
