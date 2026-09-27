// Prontuario unico do Paciente. A tabela legada prontuario permanece intacta.
table prontuario_paciente {
  auth = false
  schema {
    int id
    int paciente_id {
      table = "paciente"
    }
    timestamp aberto_em?=now
    enum situacao?=ativo {
      values = ["ativo", "inativo"]
    }
  }
  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree|unique", field: [{name: "paciente_id", op: "asc"}]}
  ]
}
