// Eventos imutáveis das transições de situação de Exame.
table exame_situacao_historico {
  auth = false
  schema {
    int id
    int exame_id {
      table = "exame"
    }
    enum? situacao_anterior? {
      values = [
        "Solicitado"
        "Realizado"
        "Resultado disponível"
        "Cancelado"
        "Não realizado"
      ]
    }
    enum situacao_nova {
      values = [
        "Solicitado"
        "Realizado"
        "Resultado disponível"
        "Cancelado"
        "Não realizado"
      ]
    }
    int conta_acesso_id {
      table = "conta_acesso"
    }
    timestamp alterado_em?=now
  }
  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "exame_id", op: "asc"}, {name: "alterado_em", op: "asc"}]}
  ]
}
