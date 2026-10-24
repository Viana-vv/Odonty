// Exames clínicos sem anexos nesta entrega; resultados permanecem no Xano.
table exame {
  int paciente_id {
    table = "paciente"
  }
  int consulta_id? {
    table = "consulta"
  }
  int profissional_id {
    table = "profissional"
  }
  text tipo
  text situacao
  date solicitado_em
  date realizado_em?
  text resultado?
  text observacoes?
  date criado_em
  indexes {
    {type: "btree", field: [{name: "paciente_id", op: "asc"}, {name: "solicitado_em", op: "desc"}]}
    {type: "btree", field: [{name: "profissional_id", op: "asc"}, {name: "solicitado_em", op: "desc"}]}
  }
}
