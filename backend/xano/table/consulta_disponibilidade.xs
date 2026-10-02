// Vínculo 1:1 aditivo: não altera nem reinterpreta a tabela legada consulta.
table consulta_disponibilidade {
  auth = false
  schema {
    int id
    int consulta_id {
      table = "consulta"
    }
    int disponibilidade_id {
      table = "disponibilidade_agenda"
    }
    timestamp criado_em?=now
  }
  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree|unique", field: [{name: "consulta_id", op: "asc"}]}
    {type: "btree|unique", field: [{name: "disponibilidade_id", op: "asc"}]}
  ]
}
