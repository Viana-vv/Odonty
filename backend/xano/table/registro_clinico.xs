// Registro longitudinal separado da tabela legada prontuario.
table registro_clinico {
  auth = false
  schema {
    int id
    int prontuario_id {
      table = "prontuario_paciente"
    }
    int paciente_id {
      table = "paciente"
    }
    int profissional_id {
      table = "profissional"
    }
    int? consulta_id? {
      table = "consulta"
    }
    text conteudo
    bool liberado_paciente?=false
    bool concluido?=true
    timestamp registrado_em?=now
  }
  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "prontuario_id", op: "asc"}, {name: "registrado_em", op: "desc"}]}
    {type: "btree", field: [{name: "paciente_id", op: "asc"}, {name: "profissional_id", op: "asc"}]}
  ]
}
