// Intervalos de Agenda; as tabelas legadas de Consulta permanecem intactas.
table disponibilidade_agenda {
  auth = false
  schema {
    int id
    int profissional_id {
      table = "profissional"
    }
    timestamp inicio
    timestamp fim
    enum situacao?="disponivel" {
      values = ["disponivel", "reservado", "bloqueado", "indisponivel"]
    }
    timestamp criado_em?=now
    timestamp? atualizado_em?
  }
  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "profissional_id", op: "asc"}, {name: "inicio", op: "asc"}]}
  ]
}
