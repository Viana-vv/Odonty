// Auditoria append-only das transições de Consulta, inclusive cancelamentos.
table consulta_situacao_historico {
  auth = false
  schema {
    int id
    int consulta_id {
      table = "consulta"
    }
    text situacao_anterior
    text situacao_nova
    int conta_acesso_id {
      table = "conta_acesso"
    }
    text? motivo?
    timestamp alterado_em?=now
  }
  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "consulta_id", op: "asc"}, {name: "alterado_em", op: "asc"}]}
    {type: "btree", field: [{name: "conta_acesso_id", op: "asc"}, {name: "alterado_em", op: "desc"}]}
  ]
  guid = "u461Vn_Sr55xxFTSVA8zlG3kUE0"
}
