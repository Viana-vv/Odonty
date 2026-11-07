// Schema LOCAL restrito, não publicado. Retenção proposta: 30 dias.
// Nenhum token/hash, senha, e-mail, link ou payload técnico neste registro.
table redefinicao_senha_auditoria {
  auth = false
  schema {
    int id
    uuid operacao_id
    int? solicitante_id? { table = "conta_acesso" }
    int conta_acesso_id { table = "conta_acesso" }
    timestamp criada_em
    enum resultado {
      values = ["reservada", "aceito", "falhou", "desconhecido", "consumido", "invalidado", "substituido"]
    }
  }
  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "operacao_id", op: "asc"}]}
  ]
}
