// Especialidades odontologicas
table especialidade {
  auth = false

  schema {
    int id
    timestamp criado_em?=now
    text nome filters=trim
    text? descricao?
    bool ativo?=true
  }

  index = [{type: "primary", field: [{name: "id"}]}]
  guid = "0JUCTTdbbvXvkKRJoJU1hzqe49M"
}
