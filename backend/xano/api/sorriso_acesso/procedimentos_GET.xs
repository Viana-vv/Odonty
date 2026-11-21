// Listagem administrativa independente das opções da Agenda.
query "procedimentos" verb=GET {
  api_group = "Sorriso Acesso"
  auth = "conta_acesso"
  input { }
  stack {
    util.set_header {
      value = "Cache-Control: no-store"
      duplicates = "replace"
    }
    function.run sorriso_validar_sessao {
      input = {conta_id: $auth.id, sessao_id: $auth.extras.sessao_id}
    } as $sessao
    db.get conta_acesso {
      field_name = "id"
      field_value = $auth.id
      output = ["id", "perfis", "situacao"]
    } as $solicitante
    conditional {
      if ($solicitante == null || $solicitante.situacao != "ativo" || ($solicitante.perfis|intersect:["administrador", "recepcionista"]|count) == 0) {
        util.set_header { value = "HTTP/1.1 403 Forbidden" }
        return { value = {codigo: "ACESSO_NEGADO", mensagem: "Listagem de Procedimentos disponível somente à equipe administrativa."} }
      }
    }
    db.query procedimento {
      where = $db.procedimento.ativo == true
      sort = {procedimento.nome: "asc", procedimento.id: "asc"}
      return = {type: "list"}
      output = ["id", "nome"]
    } as $procedimentos
  }
  response = {procedimentos: $procedimentos}
  history = false
  guid = "DLcLIje7DKxYON4AlHsoc4_cbKc"
}
