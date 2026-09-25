// Profissionais da clinica Sorriso+
table profissional {
  auth = false

  schema {
    int id
    timestamp criado_em?=now
    text nome filters=trim
    text cro filters=trim
    text? telefone? filters=trim
    email? email? filters=trim|lower
    int? usuario_id? {
      table = "usuario"
    }
  
    int especialidade_id {
      table = "especialidade"
    }
  
    enum situacao?=Ativo {
      values = ["Ativo", "Inativo"]
    }
  
    int? conta_acesso_id? filters=@:"dbo=897322" {
      table = "conta_acesso"
    }
  
    timestamp? atualizado_em?
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree|unique", field: [{name: "cro", op: "asc"}]}
    {
      type : "btree|unique"
      field: [{name: "conta_acesso_id", op: "asc"}]
    }
  ]
  guid = "mLNQgWXy4uujUBnEF8tbNK7_Ie8"
}
