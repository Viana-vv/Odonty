"""Repositório fictício, volátil e isolado por sessão para demonstrações."""

from copy import deepcopy
from datetime import date, datetime, time, timedelta

CHAVE_DADOS = "sorrisomais_demo_dados"
STATUS_ATIVOS = {"Agendada", "Confirmada", "Em atendimento"}
STATUS_FINAIS = {"Realizada", "Cancelada", "Falta"}


def _dados_iniciais(hoje):
    pacientes = [
        {"id": 1, "nome": "Marina Costa", "cpf": "000.000.000-01", "nascimento": "1992-04-12",
         "telefone": "(11) 90000-0001", "email": "marina@example.com", "celular": "(11) 90000-0001",
         "situacao": "ativo", "observacoes": "", "prontuario_id": 1},
        {"id": 2, "nome": "Carlos Henrique", "cpf": "000.000.000-02", "nascimento": "1987-09-23",
         "telefone": "(11) 90000-0002", "email": "carlos@example.com", "celular": "(11) 90000-0002",
         "situacao": "ativo", "observacoes": "", "prontuario_id": 2},
        {"id": 3, "nome": "Bianca Alves", "cpf": "000.000.000-03", "nascimento": "1996-02-08",
         "telefone": "(11) 90000-0003", "email": "bianca@example.com", "celular": "(11) 90000-0003",
         "situacao": "ativo", "observacoes": "", "prontuario_id": 3},
    ]
    profissionais = [
        {"id": 1, "nome": "Juliana Martins", "especialidade": "Clínica geral", "cro": "SP-000001",
         "telefone": "(11) 90000-0101", "email": "juliana@example.com", "situacao": "ativo"},
        {"id": 2, "nome": "Marcelo Ferreira", "especialidade": "Ortodontia", "cro": "SP-000002",
         "telefone": "(11) 90000-0102", "email": "marcelo@example.com", "situacao": "ativo"},
    ]
    procedimentos = [
        {"id": 1, "nome": "Avaliação", "duracao_minutos": 30, "valor_referencia": 120.0, "situacao": "ativo"},
        {"id": 2, "nome": "Limpeza e profilaxia", "duracao_minutos": 45, "valor_referencia": 180.0, "situacao": "ativo"},
        {"id": 3, "nome": "Restauração em resina", "duracao_minutos": 60, "valor_referencia": 320.0, "situacao": "ativo"},
        {"id": 4, "nome": "Manutenção ortodôntica", "duracao_minutos": 30, "valor_referencia": 190.0, "situacao": "ativo"},
        {"id": 5, "nome": "Tratamento de canal", "duracao_minutos": 90, "valor_referencia": 850.0, "situacao": "ativo"},
        {"id": 6, "nome": "Clareamento", "duracao_minutos": 60, "valor_referencia": 650.0, "situacao": "ativo"},
    ]
    data = hoje.isoformat()
    consultas = [
        {"id": 1, "paciente_id": 1, "profissional_id": 1, "procedimento_id": 1, "data": data,
         "hora": "08:00", "situacao": "Falta", "observacoes": "", "criada_por": "Demonstração"},
        {"id": 2, "paciente_id": 2, "profissional_id": 1, "procedimento_id": 2, "data": data,
         "hora": "09:30", "situacao": "Confirmada", "observacoes": "", "criada_por": "Demonstração"},
        {"id": 3, "paciente_id": 3, "profissional_id": 2, "procedimento_id": 1, "data": data,
         "hora": "10:00", "situacao": "Agendada", "observacoes": "", "criada_por": "Demonstração"},
        {"id": 4, "paciente_id": 3, "profissional_id": 2, "procedimento_id": 4, "data": data,
         "hora": "11:00", "situacao": "Agendada", "observacoes": "", "criada_por": "Demonstração"},
        {"id": 5, "paciente_id": 1, "profissional_id": 2, "procedimento_id": 5, "data": data,
         "hora": "13:00", "situacao": "Agendada", "observacoes": "", "criada_por": "Demonstração"},
        {"id": 6, "paciente_id": 2, "profissional_id": 1, "procedimento_id": 3,
         "data": (hoje + timedelta(days=1)).isoformat(), "hora": "09:00", "situacao": "Agendada",
         "observacoes": "", "criada_por": "Demonstração"},
    ]
    registros = [
        {"id": 1, "prontuario_id": 1, "paciente_id": 1, "consulta_id": 1, "profissional_id": 1,
         "data": data, "procedimento": "Avaliação", "evolucao": "Registro fictício para demonstração."},
        {"id": 2, "prontuario_id": 2, "paciente_id": 2, "consulta_id": 2, "profissional_id": 1,
         "data": data, "procedimento": "Limpeza e profilaxia", "evolucao": "Registro fictício para demonstração."},
    ]
    return {"pacientes": pacientes, "profissionais": profissionais,
            "procedimentos": procedimentos, "consultas": consultas,
            "registros_clinicos": registros}


class RepositorioDemonstracao:
    """Mantém dados fictícios no estado da sessão; nunca acessa rede ou disco."""

    def __init__(self, estado_sessao, hoje=None):
        self._estado = estado_sessao
        if CHAVE_DADOS not in estado_sessao:
            self._estado[CHAVE_DADOS] = _dados_iniciais(hoje or date.today())

    @property
    def dados(self):
        return self._estado[CHAVE_DADOS]

    def listar(self, entidade):
        return deepcopy(self.dados[entidade])

    def buscar_pacientes(self, termo=""):
        termo = (termo or "").strip().casefold()
        itens = self.listar("pacientes")
        return [p for p in itens if not termo or any(
            termo in str(p.get(campo, "")).casefold()
            for campo in ("nome", "cpf", "telefone", "email")
        )]

    def salvar_paciente(self, campos, paciente_id=None):
        nome = str(campos.get("nome", "")).strip()
        if len(nome) < 2:
            raise ValueError("Informe o nome completo do Paciente.")
        cpf = str(campos.get("cpf", "")).strip()
        if not cpf:
            raise ValueError("Informe o CPF fictício do Paciente.")
        for item in self.dados["pacientes"]:
            if item["cpf"] == cpf and item["id"] != paciente_id:
                raise ValueError("Este CPF fictício já está cadastrado na demonstração.")
        if paciente_id:
            paciente = next((p for p in self.dados["pacientes"] if p["id"] == paciente_id), None)
            if not paciente:
                raise ValueError("Paciente não encontrado na demonstração.")
            paciente.update({k: v for k, v in campos.items() if k in {
                "nome", "cpf", "nascimento", "telefone", "email", "celular", "observacoes"
            }})
            paciente["nome"] = nome
            return paciente_id
        novo_id = max((p["id"] for p in self.dados["pacientes"]), default=0) + 1
        prontuario_id = max((p["prontuario_id"] for p in self.dados["pacientes"]), default=0) + 1
        self.dados["pacientes"].append({
            "id": novo_id, "nome": nome, "cpf": cpf,
            "nascimento": str(campos.get("nascimento", "")),
            "telefone": str(campos.get("telefone", "")),
            "email": str(campos.get("email", "")),
            "celular": str(campos.get("celular", "")),
            "observacoes": str(campos.get("observacoes", "")),
            "situacao": "ativo", "prontuario_id": prontuario_id,
        })
        return novo_id

    def salvar_profissional(self, campos):
        nome = str(campos.get("nome", "")).strip()
        if len(nome) < 2:
            raise ValueError("Informe o nome completo do Profissional.")
        novo_id = max((p["id"] for p in self.dados["profissionais"]), default=0) + 1
        self.dados["profissionais"].append({
            "id": novo_id, "nome": nome,
            "especialidade": str(campos.get("especialidade", "")).strip(),
            "cro": str(campos.get("cro", "")).strip().upper(),
            "telefone": str(campos.get("telefone", "")).strip(),
            "email": str(campos.get("email", "")).strip(), "situacao": "ativo",
        })
        return novo_id

    def alterar_situacao_profissional(self, profissional_id, ativo):
        profissional = next((p for p in self.dados["profissionais"] if p["id"] == profissional_id), None)
        if not profissional:
            raise ValueError("Profissional não encontrado na demonstração.")
        profissional["situacao"] = "ativo" if ativo else "inativo"

    def agendar_consulta(self, paciente_id, profissional_id, procedimento_id, data, hora, observacoes=""):
        paciente = next((p for p in self.dados["pacientes"] if p["id"] == paciente_id), None)
        profissional = next((p for p in self.dados["profissionais"] if p["id"] == profissional_id), None)
        procedimento = next((p for p in self.dados["procedimentos"] if p["id"] == procedimento_id), None)
        if not paciente or not profissional or not procedimento:
            raise ValueError("Selecione um Paciente, Profissional e Procedimento disponíveis.")
        if profissional["situacao"] != "ativo":
            raise ValueError("Profissional inativo não pode receber nova Consulta.")
        try:
            dia = date.fromisoformat(str(data))
            inicio = datetime.combine(dia, time.fromisoformat(str(hora)))
        except ValueError:
            raise ValueError("Informe uma data e horário válidos.") from None
        fim = inicio + timedelta(minutes=procedimento["duracao_minutos"])
        if inicio < datetime.combine(date.today(), time.min):
            raise ValueError("Não é possível agendar uma Consulta demonstrativa no passado.")
        if inicio.time() < time(8) or fim.time() > time(18):
            raise ValueError("A agenda demonstrativa funciona entre 08:00 e 18:00.")
        for existente in self.dados["consultas"]:
            if existente["situacao"] not in STATUS_ATIVOS or existente["data"] != dia.isoformat():
                continue
            proc_existente = next(p for p in self.dados["procedimentos"]
                                  if p["id"] == existente["procedimento_id"])
            inicio_existente = datetime.combine(dia, time.fromisoformat(existente["hora"]))
            fim_existente = inicio_existente + timedelta(minutes=proc_existente["duracao_minutos"])
            sobreposicao = inicio < fim_existente and inicio_existente < fim
            if sobreposicao and existente["profissional_id"] == profissional_id:
                raise ValueError("Este horário conflita com outra Consulta do Profissional.")
            if sobreposicao and existente["paciente_id"] == paciente_id:
                raise ValueError("Este Paciente já tem uma Consulta neste horário.")
        novo_id = max((c["id"] for c in self.dados["consultas"]), default=0) + 1
        self.dados["consultas"].append({
            "id": novo_id, "paciente_id": paciente_id, "profissional_id": profissional_id,
            "procedimento_id": procedimento_id, "data": dia.isoformat(), "hora": inicio.strftime("%H:%M"),
            "situacao": "Agendada", "observacoes": str(observacoes).strip(),
            "criada_por": "Demonstração",
        })
        return novo_id

    def alterar_situacao_consulta(self, consulta_id, situacao):
        permitidos = {"Agendada", "Confirmada", "Em atendimento", "Realizada", "Cancelada", "Falta"}
        if situacao not in permitidos:
            raise ValueError("Situação de Consulta inválida.")
        consulta = next((c for c in self.dados["consultas"] if c["id"] == consulta_id), None)
        if not consulta:
            raise ValueError("Consulta não encontrada na demonstração.")
        consulta["situacao"] = situacao

    def listar_registros_clinicos(self, perfis, paciente_id=None):
        if "profissional" not in set(perfis):
            raise PermissionError("Somente Profissional autorizado pode acessar dados clínicos.")
        registros = self.listar("registros_clinicos")
        if paciente_id is not None:
            registros = [r for r in registros if r["paciente_id"] == paciente_id]
        return sorted(registros, key=lambda r: (r["data"], r["id"]), reverse=True)

    def registrar_evolucao(self, perfis, paciente_id, profissional_id, data, procedimento, evolucao):
        if "profissional" not in set(perfis):
            raise PermissionError("Somente Profissional autorizado pode registrar evolução clínica.")
        paciente = next((p for p in self.dados["pacientes"] if p["id"] == paciente_id), None)
        profissional = next((p for p in self.dados["profissionais"] if p["id"] == profissional_id), None)
        if not paciente or not profissional:
            raise ValueError("Selecione um Paciente e Profissional disponíveis.")
        if not str(procedimento).strip() or not str(evolucao).strip():
            raise ValueError("Preencha o Procedimento e a evolução clínica.")
        try:
            dia = date.fromisoformat(str(data))
        except ValueError:
            raise ValueError("Informe uma data válida.") from None
        novo_id = max((r["id"] for r in self.dados["registros_clinicos"]), default=0) + 1
        self.dados["registros_clinicos"].append({
            "id": novo_id, "prontuario_id": paciente["prontuario_id"],
            "paciente_id": paciente_id, "consulta_id": None, "profissional_id": profissional_id,
            "data": dia.isoformat(), "procedimento": str(procedimento).strip(),
            "evolucao": str(evolucao).strip(),
        })
        return novo_id

    def metricas(self, dia):
        consultas = [c for c in self.dados["consultas"] if c["data"] == dia.isoformat()]
        return {
            "consultas": len(consultas),
            "aguardando": sum(c["situacao"] == "Agendada" for c in consultas),
            "realizadas": sum(c["situacao"] == "Realizada" for c in consultas),
            "pacientes": sum(p["situacao"] == "ativo" for p in self.dados["pacientes"]),
            "confirmadas": sum(c["situacao"] == "Confirmada" for c in consultas),
        }

