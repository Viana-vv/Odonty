// Operações temporárias de recuperação; o OTP nunca é armazenado em texto puro.
table recuperacao_senha {
  schema {
    int id
    text operacao_id
    email email filters=trim|lower
    password otp_hash
    timestamp expira_em
    int tentativas?=0
    bool validado?=false
    bool utilizado?=false
    timestamp criado_em?=now
  }
  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree|unique", field: [{name: "operacao_id", op: "asc"}]}
  ]
  guid = "24li_vWKuCc0o6Wa9XO_qyRW6UI"
}
