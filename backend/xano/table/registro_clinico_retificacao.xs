// Cada retificacao e append-only e preserva o Registro Clínico original.
table registro_clinico_retificacao {
  auth = false
  schema {
    int id
    int registro_clinico_id {
      table = "registro_clinico"
    }
    int profissional_id {
      table = "profissional"
    }
    text conteudo
    text justificativa
    timestamp criada_em?=now
  }
  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "registro_clinico_id", op: "asc"}, {name: "criada_em", op: "asc"}]}
  ]
}
