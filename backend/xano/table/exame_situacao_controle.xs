// Linha de serialização das transições de situação de um Exame.
table exame_situacao_controle {
  auth = false
  schema {
    int id
    int exame_id {
      table = "exame"
    }
    int versao?=0
    timestamp atualizado_em?=now
  }
  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree|unique", field: [{name: "exame_id", op: "asc"}]}
  ]
}
