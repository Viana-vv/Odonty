// Comprovante idempotente de cadastro de Paciente
table cadastro_paciente_operacao {
  auth = false

  schema {
    int id
    int conta_acesso_id {
      table = "conta_acesso"
    }
  
    text operacao_id
    text impressao_hmac
    int paciente_id {
      table = "paciente"
    }
  
    timestamp criado_em?=now
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {
      type : "btree|unique"
      field: [
        {name: "conta_acesso_id", op: "asc"}
        {name: "operacao_id", op: "asc"}
      ]
    }
  ]
}