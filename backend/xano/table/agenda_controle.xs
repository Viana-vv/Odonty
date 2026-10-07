// Linha de serializacao por Profissional/Paciente, atualizada dentro da transacao.
table agenda_controle {
  auth = false
  schema {
    int id
    enum escopo {
      values = ["profissional", "paciente"]
    }
    int escopo_id
    int versao?=0
    timestamp atualizado_em?=now
  }
  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree|unique", field: [{name: "escopo", op: "asc"}, {name: "escopo_id", op: "asc"}]}
  ]
  guid = "mQMG6ePSTs9TR9NfMsCevc_MQVE"
}
