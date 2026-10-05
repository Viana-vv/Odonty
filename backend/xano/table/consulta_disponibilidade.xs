// Cada Consulta possui no máximo uma Disponibilidade. A mesma Disponibilidade
// pode aparecer em Consultas históricas canceladas antes de ser reutilizada.
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
    {type: "btree", field: [{name: "disponibilidade_id", op: "asc"}]}
  ]
}
