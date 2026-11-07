// Schema LOCAL, não publicado. Não é primitiva de lock/CAS.
// Cotas usam reservas da operação em janela móvel, nunca somente cache frontend.
// Uma linha por conta mantém geração monotônica; inclusão requer coordenação real.
table redefinicao_senha_controle {
  auth = false
  schema {
    int id
    int conta_acesso_id { table = "conta_acesso" }
    int geracao?=0
  }
  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree|unique", field: [{name: "conta_acesso_id", op: "asc"}]}
  ]
}
