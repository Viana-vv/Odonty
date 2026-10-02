// Pacientes da clinica Sorriso+
table paciente {
  auth = false

  schema {
    int id
    timestamp criado_em?=now
    text nome filters=trim
    text? cpf? filters=trim
    text telefone filters=trim
    email? email? filters=trim|lower
    date? data_nascimento?
    text? observacoes?
  
    // Celular obrigatorio para novos cadastros; contatos existentes permanecem inalterados
    text? celular?

    // Ligacao opcional usada para limitar operacoes do proprio Paciente.
    int? conta_acesso_id? {
      table = "conta_acesso"
    }
  
    // Situacao do Paciente; novos cadastros sao ativos, sem classificar legados automaticamente.
    enum? situacao? {
      values = ["ativo", "inativo"]
    }
  
    timestamp? atualizado_em?
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree|unique", field: [{name: "cpf", op: "asc"}]}
    {type: "btree|unique", field: [{name: "conta_acesso_id", op: "asc"}]}
  ]
}
