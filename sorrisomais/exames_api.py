"""Cliente REST isolado para o fluxo de Exames; não registra dados clínicos."""

from datetime import date

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
        if not isinstance(paciente_id, int) or isinstance(paciente_id, bool) or paciente_id <= 0:
            raise ErroAcesso("Selecione um Paciente.", 400)
        if not isinstance(consulta_id, int) or isinstance(consulta_id, bool) or consulta_id <= 0:
            raise ErroAcesso("Selecione uma Consulta.", 400)
        if not isinstance(tipo, str) or not tipo.strip() or len(tipo.strip()) > 160:
            raise ErroAcesso("Informe o tipo do exame.", 400)
        if not isinstance(solicitado_em, str):
            raise ErroAcesso("Informe uma data de solicitação válida.", 400)
        try:
            data_solicitacao = date.fromisoformat(solicitado_em)
        except ValueError:
            raise ErroAcesso("Informe uma data de solicitação válida.", 400) from None
        if data_solicitacao > date.today():
            raise ErroAcesso("A data da solicitação não pode estar no futuro.", 400)
        if observacoes is not None and (not isinstance(observacoes, str) or len(observacoes.strip()) > 1000):
            raise ErroAcesso("As observações devem ter no máximo 1000 caracteres.", 400)
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
