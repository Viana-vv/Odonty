// Vínculo append-only entre a Consulta preservada e sua substituta.
table consulta_reagendamento {
  auth = false
  schema {
    int id
    int consulta_original_id {
      table = "consulta"
    }
    int consulta_nova_id {
      table = "consulta"
    }
    int conta_acesso_id {
      table = "conta_acesso"
    }
    text justificativa
    timestamp criado_em?=now
  }
  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree|unique", field: [{name: "consulta_original_id", op: "asc"}]}
    {type: "btree|unique", field: [{name: "consulta_nova_id", op: "asc"}]}
  ]
  guid = "consultaReagendamento64v1"
}
