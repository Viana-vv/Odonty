"""Cliente REST isolado para o fluxo de Exames; não registra dados clínicos."""

from .api import ErroAcesso


SITUACOES_EXAME = ("Solicitado", "Realizado", "Resultado disponível", "Cancelado", "Não realizado")


class ClienteExames:
    def __init__(self, cliente):
        self.cliente = cliente

    def listar(self, token, *, paciente_id=None, consulta_id=None):
        params = {}
        if paciente_id is not None:
            params["paciente_id"] = paciente_id
        if consulta_id is not None:
            params["consulta_id"] = consulta_id
        data = self.cliente._request("GET", "/exames", token=token, params=params or None)
        exames = data.get("exames") if isinstance(data, dict) else None
        if not isinstance(exames, list):
            raise ErroAcesso()
        return [item for item in exames if isinstance(item, dict)]

    def solicitar(self, token, *, paciente_id, consulta_id, tipo, solicitado_em, observacoes=None):
        if not isinstance(tipo, str) or not tipo.strip() or len(tipo.strip()) > 160:
            raise ErroAcesso("Informe o tipo do exame.", 400)
        payload = {"paciente_id": paciente_id, "consulta_id": consulta_id,
                   "tipo": tipo.strip(), "solicitado_em": solicitado_em}
        if observacoes:
            payload["observacoes"] = observacoes.strip()
        data = self.cliente._request("POST", "/exames", token=token, payload=payload, status_esperado=201)
        exame = data.get("exame") if isinstance(data, dict) else None
        if not isinstance(exame, dict):
            raise ErroAcesso()
        return exame

    def atualizar_situacao(self, token, exame_id, *, situacao, resultado=None, realizado_em=None, observacoes=None):
        if situacao not in SITUACOES_EXAME:
            raise ErroAcesso("Situação de exame inválida.", 400)
        payload = {"situacao": situacao}
        if resultado is not None:
            payload["resultado"] = resultado.strip()
        if realizado_em is not None:
            payload["realizado_em"] = realizado_em
        if observacoes is not None:
            payload["observacoes"] = observacoes.strip()
        data = self.cliente._request("PATCH", f"/exames/{int(exame_id)}/situacao", token=token, payload=payload)
        exame = data.get("exame") if isinstance(data, dict) else None
        if not isinstance(exame, dict):
            raise ErroAcesso()
        return exame
