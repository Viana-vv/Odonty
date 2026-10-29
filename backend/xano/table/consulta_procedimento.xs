// Relação N:N aditiva; campos de criação e profissional_id guardam o planejamento.
table consulta_procedimento {
  auth = false
  schema {
    int id
    int consulta_id {
      table = "consulta"
    }
    int procedimento_id {
      table = "procedimento"
    }
    int? profissional_id? {
      table = "profissional"
    }
    timestamp criado_em?=now
    enum situacao?=planejado {
      values = [
        "planejado"
        "autorizado"
        "realizado"
        "cancelado"
      ]
    }
    int? realizado_por_profissional_id? {
      table = "profissional"
    }
    timestamp? realizado_em?
  }
  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree|unique", field: [{name: "consulta_id", op: "asc"}, {name: "procedimento_id", op: "asc"}]}
  ]
  guid = "-cnTW6TMgS-QZ98eQwKI508wFIU"
}
