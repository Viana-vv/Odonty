// Sessões revogáveis da Conta de Acesso; não armazena tokens.
table sessao_acesso {
  auth = false
  schema {
    uuid id
    int conta_acesso_id { table = "conta_acesso" }
    timestamp criada_em?=now
    timestamp expira_em
    timestamp? revogada_em?
  }
  index = [{type: "primary", field: [{name: "id"}]}]
  guid = "6Mb0f4MVouTTQ53i7ax_FShsA3A"
}

