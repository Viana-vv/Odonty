// Exames clínicos sem anexos nesta entrega; resultados permanecem no Xano.
table exame {
  auth = false
  schema {
    int id
    int paciente_id {
      table = "paciente"
    }
    int? consulta_id? {
      table = "consulta"
    }
    int profissional_id {
      table = "profissional"
    }
    text tipo
    enum situacao?=Solicitado {
      values = [
        "Solicitado"
        "Realizado"
        "Resultado disponível"
        "Cancelado"
        "Não realizado"
      ]
    }
    timestamp solicitado_em
    timestamp? realizado_em?
    text? resultado?
    text? observacoes?
    timestamp criado_em?=now
  }
  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "paciente_id", op: "asc"}, {name: "solicitado_em", op: "desc"}]}
    {type: "btree", field: [{name: "profissional_id", op: "asc"}, {name: "solicitado_em", op: "desc"}]}
  ]
}
