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
  
    // Situacao do Paciente; novos cadastros sao ativos, sem classificar legados automaticamente.
    enum? situacao? {
      values = ["ativo", "inativo"]
    }
  
    timestamp? atualizado_em?
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree|unique", field: [{name: "cpf", op: "asc"}]}
  ]
}