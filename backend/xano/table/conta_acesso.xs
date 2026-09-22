// Conta de Acesso interna, independente da tabela legada usuario.
table conta_acesso {
  auth = true
  schema {
    int id
    timestamp criado_em?=now
    text nome filters=trim
    email email filters=trim|lower
    password senha
    enum[] perfis {
      values = ["administrador", "recepcionista", "profissional", "paciente"]
    }
    enum situacao?="ativo" {
      values = ["ativo", "inativo", "bloqueado"]
    }
  }
  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree|unique", field: [{name: "email", op: "asc"}]}
  ]
  guid = "5iW9jN3I16_1AtC_p9xFApHwQUg"
}

