"""Cliente REST dedicado aos Procedimentos vinculados a Consultas."""

import requests

from .api import ErroAcesso
from .config import Configuracao

_MENSAGEM_INDISPONIVEL = "Não foi possível carregar os Procedimentos. Tente novamente em instantes."
_MENSAGENS_STATUS = {
    400: "Confira a Consulta e tente novamente.",
    401: "Sua sessão expirou ou não é válida. Entre novamente.",
    403: "Sua conta não tem permissão para acessar estes Procedimentos.",
    404: "A Consulta ou o Procedimento não foi encontrado no escopo permitido.",
    409: "O Procedimento mudou. Atualize a lista e tente novamente.",
    429: "Muitas tentativas. Aguarde um pouco antes de tentar novamente.",
}


def _validar_id(valor):
    if isinstance(valor, bool) or not isinstance(valor, int) or valor <= 0:
        raise ErroAcesso("A Consulta informada é inválida.", 400)
    return valor


class ClienteProcedimentosConsulta:
    """Executa os dois contratos REST sem registrar tokens ou dados clínicos."""

    def __init__(self, configuracao: Configuracao):
        self.configuracao = configuracao

    def _solicitar(self, metodo, rota, token):
        if not isinstance(token, str) or not token or any(caractere.isspace() for caractere in token):
            raise ErroAcesso("Sua sessão não é válida. Entre novamente.", 401)
        try:
            resposta = requests.request(
                metodo,
                self.configuracao.api_base_url + rota,
                headers={"Accept": "application/json", "Authorization": f"Bearer {token}"},
                timeout=self.configuracao.timeout,
                allow_redirects=False,
            )
        except requests.RequestException:
            raise ErroAcesso(_MENSAGEM_INDISPONIVEL) from None
        with resposta:
            if resposta.status_code != 200:
                raise ErroAcesso(
                    _MENSAGENS_STATUS.get(resposta.status_code, _MENSAGEM_INDISPONIVEL),
                    resposta.status_code,
                )
            try:
                corpo = resposta.json()
            except ValueError:
                raise ErroAcesso(_MENSAGEM_INDISPONIVEL) from None
        if not isinstance(corpo, dict):
            raise ErroAcesso(_MENSAGEM_INDISPONIVEL)
        return corpo

    def listar_procedimentos_consulta(self, token, consulta_id):
        consulta_id = _validar_id(consulta_id)
        corpo = self._solicitar("GET", f"/consultas/{consulta_id}/procedimentos", token)
        procedimentos = corpo.get("procedimentos")
        if not isinstance(procedimentos, list) or any(not isinstance(item, dict) for item in procedimentos):
            raise ErroAcesso(_MENSAGEM_INDISPONIVEL)
        return procedimentos

    def marcar_procedimento_realizado(self, token, consulta_id, consulta_procedimento_id):
        consulta_id = _validar_id(consulta_id)
        consulta_procedimento_id = _validar_id(consulta_procedimento_id)
        rota = (
            f"/consultas/{consulta_id}/procedimentos/"
            f"{consulta_procedimento_id}/realizacao"
        )
        corpo = self._solicitar("PATCH", rota, token)
        procedimento = corpo.get("procedimento")
        if not isinstance(procedimento, dict):
            raise ErroAcesso(_MENSAGEM_INDISPONIVEL)
        return procedimento
