"""Contrato REST do Xano. Nunca registra payloads ou credenciais."""

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone

import requests

from .config import Configuracao

ROTULOS = {"administrador": "Administrador", "recepcionista": "Recepcionista", "profissional": "Dentista"}
PERFIS_DOMINIO = set(ROTULOS) | {"paciente"}
INDISPONIVEL = "Não foi possível conectar ao serviço. Tente novamente em instantes."


class ErroAcesso(Exception):
    def __init__(self, mensagem=INDISPONIVEL, status=None, codigo=None):
        super().__init__(mensagem)
        self.status = status
        self.codigo = codigo


@dataclass(frozen=True)
class Credencial:
    token: str = field(repr=False)
    expira_em: datetime


@dataclass(frozen=True)
class ContaAcesso:
    id: int
    nome: str
    perfis: tuple[str, ...]
    expira_em: datetime


def validar_campos(email, senha):
    email = email.strip().lower()
    if not email or not senha:
        raise ErroAcesso("Preencha o e-mail e a senha.", 400)
    if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
        raise ErroAcesso("Informe um e-mail válido.", 400)
    return email


def ler_validade(value):
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|\+00:00)", value):
        raise ErroAcesso()
    try:
        expiration = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        raise ErroAcesso() from None
    if expiration <= datetime.now(timezone.utc):
        raise ErroAcesso("Sua sessão expirou. Entre novamente.", 401)
    return expiration


class ClienteXano:
    def __init__(self, configuracao: Configuracao):
        self.configuracao = configuracao

    def _request(self, method, route, token=None, payload=None, status_esperado=200, params=None):
        headers = {"Accept": "application/json"}
        if token:
            if not isinstance(token, str) or any(c.isspace() for c in token):
                raise ErroAcesso("Sua sessão não é válida. Entre novamente.", 401)
            headers["Authorization"] = f"Bearer {token}"
        try:
            response = requests.request(
                method, self.configuracao.api_base_url + route,
                json=payload, headers=headers, timeout=self.configuracao.timeout,
                allow_redirects=False, params=params,
            )
        except requests.RequestException:
            raise ErroAcesso() from None
        with response:
            status = response.status_code
            if route == "/auth/logout" and status in (204, 401):
                return None
            if status != status_esperado:
                if route == "/pacientes" and status == 409:
                    try:
                        corpo = response.json()
                    except ValueError:
                        corpo = None
                    codigo = corpo.get("codigo") if isinstance(corpo, dict) else None
                    conflitos = {
                        "CPF_DUPLICADO": "CPF já cadastrado.",
                        "OPERACAO_CONFLITANTE": "Esta operação já foi usada com outros dados. Confira o resultado com o responsável pelo sistema.",
                    }
                    if isinstance(codigo, str) and codigo in conflitos:
                        raise ErroAcesso(conflitos[codigo], status, codigo)
                    raise ErroAcesso()
                messages = {
                    400: "Confira os dados informados e tente novamente.",
                    401: ("E-mail ou senha incorretos, ou conta indisponível."
                          if route == "/auth/login" else "Sua sessão expirou ou não é válida. Entre novamente."),
                    403: "Sua conta não tem permissão para acessar esta área.",
                    409: "E-mail ou CRO já cadastrado.",
                    404: "O recurso solicitado não foi encontrado.",
                    429: "Muitas tentativas. Aguarde um pouco antes de tentar novamente.",
                }
                if status == 409:
                    if route == "/consultas":
                        message = "Este horário não está mais disponível. Escolha outro."
                    elif route.startswith("/disponibilidades/"):
                        message = "Não foi possível atualizar este horário. Confira a Agenda e tente novamente."
                    elif route.startswith("/consultas/"):
                        message = "Não foi possível atualizar a Consulta. Confira a situação e tente novamente."
                    elif route.startswith("/registros-clinicos"):
                        message = "Não foi possível concluir a operação clínica. Confira o Registro e tente novamente."
                    else:
                        message = messages[409]
                    raise ErroAcesso(message, status)
                raise ErroAcesso(messages.get(status, INDISPONIVEL), status)
            try:
                data = response.json()
            except ValueError:
                raise ErroAcesso() from None
            if not isinstance(data, dict):
                raise ErroAcesso()
            return data

    def entrar(self, email, senha):
        email = validar_campos(email, senha)
        data = self._request("POST", "/auth/login", payload={"email": email, "senha": senha})
        token = data.get("token")
        if (not isinstance(token, str) or not token or any(c.isspace() for c in token)
                or data.get("tipo_token") != "Bearer"):
            raise ErroAcesso()
        return Credencial(token, ler_validade(data.get("expira_em")))

    def identificar(self, token):
        data = self._request("GET", "/auth/me", token=token)
        account = data.get("conta")
        if not isinstance(account, dict):
            raise ErroAcesso()
        profiles = account.get("perfis")
        if (type(account.get("id")) is not int or account["id"] <= 0
                or not isinstance(account.get("nome"), str) or not account["nome"].strip()
                or not isinstance(profiles, list) or not profiles
                or any(not isinstance(p, str) or p not in PERFIS_DOMINIO for p in profiles)
                or len(set(profiles)) != len(profiles)):
            raise ErroAcesso()
        if account.get("situacao") != "ativo" or not set(profiles).intersection(ROTULOS):
            raise ErroAcesso("Sua conta não tem permissão para acessar esta área.", 403)
        return ContaAcesso(account["id"], account["nome"], tuple(p for p in ROTULOS if p in profiles), ler_validade(data.get("expira_em")))

    def sair(self, token):
        self._request("POST", "/auth/logout", token=token)

    def cadastrar_paciente(self, token, nome, data_nascimento, operacao_id,
                           telefone, cpf, email, celular):
        from .pacientes import validar_cadastro, validar_operacao
        if not isinstance(token, str) or not token or any(c.isspace() for c in token):
            raise ErroAcesso("Entre na sua conta para cadastrar um paciente.", 401)
        dados = validar_cadastro(nome, data_nascimento, telefone, cpf, email, celular)
        dados["operacao_id"] = validar_operacao(operacao_id)
        try:
            data = self._request("POST", "/pacientes", token=token,
                                 payload=dados, status_esperado=201)
            paciente = data.get("paciente")
            if (not isinstance(paciente, dict)
                    or type(paciente.get("id")) is not int or paciente["id"] <= 0
                    or paciente.get("nome") != dados["nome"]
                    or paciente.get("situacao") != "ativo"
                    or data.get("operacao_id") != operacao_id):
                raise ErroAcesso()
            return paciente["id"]
        except ErroAcesso as error:
            if error.status in (400, 401, 403, 409, 429):
                raise
            raise ErroAcesso(
                "Não foi possível confirmar o cadastro. Tente reenviar a mesma operação. "
                "Não há repetição automática.", error.status,
            ) from None


    def listar_especialidades(self, token):
        data = self._request("GET", "/especialidades", token=token)
        itens = data.get("especialidades")
        if not isinstance(itens, list):
            raise ErroAcesso()
        vistos = set()
        for item in itens:
            if (not isinstance(item, dict) or type(item.get("id")) is not int
                    or item["id"] <= 0 or item["id"] in vistos
                    or not isinstance(item.get("nome"), str) or not item["nome"].strip()):
                raise ErroAcesso()
            vistos.add(item["id"])
        return [{"id": item["id"], "nome": item["nome"]} for item in itens]

    def cadastrar_profissional(self, token, nome, email, senha, cro, especialidade_id):
        from .profissionais import validar_cadastro
        dados = validar_cadastro(nome, email, senha, cro, especialidade_id)
        try:
            data = self._request("POST", "/profissionais", token=token,
                                 payload=dados, status_esperado=201)
            profissional, conta = data.get("profissional"), data.get("conta")
            if not isinstance(profissional, dict) or not isinstance(conta, dict):
                raise ErroAcesso()
            especialidade = profissional.get("especialidade")
            if (type(profissional.get("id")) is not int or profissional["id"] <= 0
                    or type(conta.get("id")) is not int or conta["id"] <= 0
                    or profissional.get("nome") != dados["nome"]
                    or profissional.get("cro") != dados["cro"]
                    or profissional.get("situacao") != "ativo"
                    or conta.get("situacao") != "ativo" or conta.get("perfis") != ["profissional"]
                    or not isinstance(especialidade, dict)
                    or type(especialidade.get("id")) is not int
                    or especialidade.get("id") != especialidade_id
                    or not isinstance(especialidade.get("nome"), str)
                    or not especialidade["nome"].strip()):
                raise ErroAcesso()
            return profissional["id"]
        except ErroAcesso as error:
            if error.status in (400, 401, 403, 409, 429):
                raise
            raise ErroAcesso(
                "Não foi possível confirmar o cadastro. Não há repetição automática. "
                "Antes de tentar novamente, confira o resultado com o responsável pelo sistema.",
                error.status,
            ) from None

    @staticmethod
    def _token_obrigatorio(token):
        if not isinstance(token, str) or not token or any(c.isspace() for c in token):
            raise ErroAcesso("Entre na sua conta para continuar.", 401)

    @staticmethod
    def _item_resposta(data, chave, campos):
        item = data.get(chave)
        if not isinstance(item, dict) or type(item.get("id")) is not int or item["id"] <= 0:
            raise ErroAcesso()
        resultado = {"id": item["id"]}
        for campo, tipo in campos.items():
            valor = item.get(campo)
            if tipo is int:
                if type(valor) is not int or valor <= 0:
                    raise ErroAcesso()
            elif tipo is str:
                if not isinstance(valor, str) or not valor.strip():
                    raise ErroAcesso()
            elif tipo is bool:
                if type(valor) is not bool:
                    raise ErroAcesso()
            resultado[campo] = valor
        return resultado

    @classmethod
    def _lista_resposta(cls, data, chave, campos):
        itens = data.get(chave)
        if not isinstance(itens, list):
            raise ErroAcesso()
        vistos = set()
        resultado = []
        for item in itens:
            normalizado = cls._item_resposta({chave: item}, chave, campos)
            if normalizado["id"] in vistos:
                raise ErroAcesso()
            vistos.add(normalizado["id"])
            resultado.append(normalizado)
        return resultado

    @classmethod
    def _consultas_resposta(cls, data):
        itens = data.get("consultas")
        if not isinstance(itens, list):
            raise ErroAcesso()
        vistos = set()
        resultado = []
        campos = {"paciente_id": int, "profissional_id": int, "situacao": str,
                  "inicio_em": str, "fim_em": str}
        for item in itens:
            normalizado = cls._item_resposta({"consulta": item}, "consulta", campos)
            disponibilidade_id = item.get("disponibilidade_id")
            if disponibilidade_id is not None and (type(disponibilidade_id) is not int or disponibilidade_id <= 0):
                raise ErroAcesso()
            normalizado["disponibilidade_id"] = disponibilidade_id
            for campo in ("paciente_nome", "profissional_nome"):
                valor = item.get(campo)
                if not isinstance(valor, str) or not valor.strip():
                    raise ErroAcesso()
                normalizado[campo] = valor.strip()
            nomes = []
            for campo in ("procedimento_nome", "procedimento_vinculado_nome"):
                nome = item.get(campo)
                if nome is not None and (not isinstance(nome, str) or not nome.strip()):
                    raise ErroAcesso()
                if nome and nome.strip() not in nomes:
                    nomes.append(nome.strip())
            if normalizado["id"] in vistos:
                anterior = next(c for c in resultado if c["id"] == normalizado["id"])
                anterior["procedimentos"] = list(dict.fromkeys(anterior["procedimentos"] + nomes))
                continue
            vistos.add(normalizado["id"])
            normalizado["procedimentos"] = nomes
            resultado.append(normalizado)
        return resultado

    def listar_opcoes_agenda(self, token):
        self._token_obrigatorio(token)
        data = self._request("GET", "/agenda/opcoes", token=token)
        opcoes = {}
        for chave in ("pacientes", "profissionais", "procedimentos"):
            opcoes[chave] = self._lista_resposta(data, chave, {"nome": str})
        return opcoes

    @classmethod
    def _consulta_resposta(cls, data):
        consulta = data.get("consulta")
        if not isinstance(consulta, dict):
            raise ErroAcesso()
        resultado = cls._item_resposta({"consulta": consulta}, "consulta", {
            "paciente_id": int, "profissional_id": int, "situacao": str,
        })
        disponibilidade_id = consulta.get("disponibilidade_id")
        if disponibilidade_id is not None and (type(disponibilidade_id) is not int or disponibilidade_id <= 0):
            raise ErroAcesso()
        resultado["disponibilidade_id"] = disponibilidade_id
        return resultado

    def listar_disponibilidades(self, token, profissional_id=None, inicio=None, fim=None):
        from .contratos_clinicos import DadosContratoInvalidos, validar_data_hora, validar_id, validar_intervalo

        self._token_obrigatorio(token)
        params = {}
        if profissional_id is not None:
            params["profissional_id"] = validar_id(profissional_id, "Profissional")
        if (inicio is None) != (fim is None):
            raise DadosContratoInvalidos("Informe início e fim juntos.")
        if inicio is not None:
            params["inicio"], params["fim"] = validar_intervalo(inicio, fim)
        data = self._request("GET", "/disponibilidades", token=token, params=params or None)
        return self._lista_resposta(data, "disponibilidades", {
            "profissional_id": int, "inicio": str, "fim": str, "situacao": str,
        })

    def criar_disponibilidade(self, token, profissional_id, inicio, fim):
        from .contratos_clinicos import validar_id, validar_intervalo

        self._token_obrigatorio(token)
        inicio, fim = validar_intervalo(inicio, fim)
        payload = {"profissional_id": validar_id(profissional_id, "Profissional"),
                   "inicio": inicio, "fim": fim}
        data = self._request("POST", "/disponibilidades", token=token,
                             payload=payload, status_esperado=201)
        return self._item_resposta(data, "disponibilidade", {
            "profissional_id": int, "inicio": str, "fim": str, "situacao": str,
        })

    def atualizar_disponibilidade(self, token, disponibilidade_id, *, inicio=None, fim=None, situacao=None):
        from .contratos_clinicos import DadosContratoInvalidos, validar_id, validar_intervalo

        self._token_obrigatorio(token)
        disponibilidade_id = validar_id(disponibilidade_id, "Disponibilidade")
        payload = {}
        if (inicio is None) != (fim is None):
            raise DadosContratoInvalidos("Informe início e fim juntos.")
        if inicio is not None:
            payload["inicio"], payload["fim"] = validar_intervalo(inicio, fim)
        if situacao is not None:
            if situacao not in {"disponivel", "bloqueado"}:
                raise DadosContratoInvalidos("Informe uma situação permitida para a Disponibilidade.")
            payload["situacao"] = situacao
        if not payload:
            raise DadosContratoInvalidos("Informe ao menos um campo para atualizar.")
        data = self._request("PATCH", f"/disponibilidades/{disponibilidade_id}",
                             token=token, payload=payload)
        return self._item_resposta(data, "disponibilidade", {
            "profissional_id": int, "inicio": str, "fim": str, "situacao": str,
        })

    def agendar_consulta(self, token, paciente_id, disponibilidade_id, procedimento_ids, motivo=None):
        from .contratos_clinicos import DadosContratoInvalidos, validar_id, validar_ids_procedimentos, validar_texto

        self._token_obrigatorio(token)
        payload = {
            "paciente_id": validar_id(paciente_id, "Paciente"),
            "disponibilidade_id": validar_id(disponibilidade_id, "Disponibilidade"),
            "procedimento_ids": validar_ids_procedimentos(procedimento_ids),
        }
        if motivo is not None:
            payload["motivo"] = validar_texto(motivo, "o motivo", 1000)
        data = self._request("POST", "/consultas", token=token,
                             payload=payload, status_esperado=201)
        return self._item_resposta(data, "consulta", {
            "paciente_id": int, "profissional_id": int, "disponibilidade_id": int,
            "situacao": str,
        })

    def listar_consultas(self, token, *, paciente_id=None, profissional_id=None,
                         situacao=None, inicio=None, fim=None):
        from .contratos_clinicos import DadosContratoInvalidos, validar_data_hora, validar_id, validar_intervalo

        self._token_obrigatorio(token)
        params = {}
        for nome, valor in (("paciente_id", paciente_id), ("profissional_id", profissional_id)):
            if valor is not None:
                params[nome] = validar_id(valor, "Paciente" if nome == "paciente_id" else "Profissional")
        if situacao is not None:
            if situacao not in {"Agendada", "Confirmada", "Em atendimento", "Realizada", "Cancelada", "Falta"}:
                raise DadosContratoInvalidos("Informe uma situação válida de Consulta.")
            params["situacao"] = situacao
        if (inicio is None) != (fim is None):
            raise DadosContratoInvalidos("Informe início e fim juntos.")
        if inicio is not None:
            params["inicio"], params["fim"] = validar_intervalo(inicio, fim)
        data = self._request("GET", "/consultas", token=token, params=params or None)
        return self._consultas_resposta(data)

    def atualizar_situacao_consulta(self, token, consulta_id, nova, motivo_cancelamento=None):
        from .contratos_clinicos import DadosContratoInvalidos, SITUACOES_CONSULTA, validar_id, validar_texto

        self._token_obrigatorio(token)
        consulta_id = validar_id(consulta_id, "Consulta")
        if nova not in SITUACOES_CONSULTA:
            raise DadosContratoInvalidos("Informe uma situação válida de Consulta.")
        if nova == "Cancelada" and motivo_cancelamento is None:
            raise DadosContratoInvalidos("Informe o motivo do cancelamento.")
        payload = {"situacao": nova}
        if motivo_cancelamento is not None:
            payload["motivo_cancelamento"] = validar_texto(motivo_cancelamento, "o motivo do cancelamento", 1000)
        data = self._request("PATCH", f"/consultas/{consulta_id}/situacao", token=token, payload=payload)
        return self._consulta_resposta(data)

    def registrar_clinico(self, token, paciente_id, conteudo, *, consulta_id=None, liberado_paciente=False):
        from .contratos_clinicos import DadosContratoInvalidos, validar_id, validar_texto

        self._token_obrigatorio(token)
        if type(liberado_paciente) is not bool:
            raise DadosContratoInvalidos("Informe se o Registro Clínico foi liberado ao Paciente.")
        payload = {
            "paciente_id": validar_id(paciente_id, "Paciente"),
            "conteudo": validar_texto(conteudo, "o conteúdo clínico"),
            "liberado_paciente": liberado_paciente,
        }
        if consulta_id is not None:
            payload["consulta_id"] = validar_id(consulta_id, "Consulta")
        data = self._request("POST", "/registros-clinicos", token=token,
                             payload=payload, status_esperado=201)
        return self._item_resposta(data, "registro_clinico", {
            "paciente_id": int, "profissional_id": int, "prontuario_id": int,
            "liberado_paciente": bool,
        })

    def listar_registros_clinicos(self, token, *, paciente_id=None, consulta_id=None):
        from .contratos_clinicos import validar_id

        self._token_obrigatorio(token)
        params = {}
        if paciente_id is not None:
            params["paciente_id"] = validar_id(paciente_id, "Paciente")
        if consulta_id is not None:
            params["consulta_id"] = validar_id(consulta_id, "Consulta")
        data = self._request("GET", "/registros-clinicos", token=token, params=params or None)
        return self._lista_resposta(data, "registros_clinicos", {
            "paciente_id": int, "profissional_id": int, "prontuario_id": int,
            "conteudo": str, "liberado_paciente": bool,
        })

    def retificar_registro_clinico(self, token, registro_id, conteudo, justificativa):
        from .contratos_clinicos import validar_id, validar_texto

        self._token_obrigatorio(token)
        registro_id = validar_id(registro_id, "Registro Clínico")
        payload = {
            "conteudo": validar_texto(conteudo, "o conteúdo clínico"),
            "justificativa": validar_texto(justificativa, "a justificativa", 1000),
        }
        data = self._request("POST", f"/registros-clinicos/{registro_id}/retificacoes",
                             token=token, payload=payload, status_esperado=201)
        return self._item_resposta(data, "retificacao", {
            "registro_clinico_id": int, "profissional_id": int,
        })
