// Estrutura legada de Consultas, preservada com procedimento opcional para
// permitir Consulta sem Procedimento sem inventar nem migrar dados históricos.
table consulta {
  auth = false
  schema {
    int id
    timestamp criado_em?=now
    int paciente_id {
      table = "paciente"
    }
    int profissional_id {
      table = "profissional"
    }
    int? procedimento_id? {
      table = "procedimento"
    }
    timestamp inicio_em
    timestamp fim_em
    enum situacao?=Agendada {
      values = [
        "Agendada"
        "Confirmada"
        "Em atendimento"
        "Concluída"
        "Cancelada"
        "Falta"
      ]
    }
    text? observacoes?
  }
  index = [{type: "primary", field: [{name: "id"}]}]
  guid = "E3f5TSHDYD3e8wWje55zTsStjt0"
}
