// Altera a situação sem apagar o Procedimento ou seus vínculos históricos.
query "procedimentos/{id}/situacao" verb=PATCH {
  api_group = "Sorriso Acesso"
  auth = "conta_acesso"
  input { int id }
  stack {
    util.set_header { value = "Cache-Control: no-store" duplicates = "replace" }
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
        return { value = {codigo: "ACESSO_NEGADO", mensagem: "Alteração permitida somente à equipe administrativa."} }
      }
    }
    db.get procedimento {
      field_name = "id"
      field_value = $input.id
      output = ["id", "nome", "ativo"]
    } as $existente
    conditional {
      if ($existente == null) {
        util.set_header { value = "HTTP/1.1 404 Not Found" }
        return { value = {codigo: "RECURSO_NAO_ENCONTRADO", mensagem: "Procedimento não encontrado."} }
      }
    }
    try_catch {
      try { util.get_raw_input { encoding = "json" } as $bruto }
      catch {
        util.set_header { value = "HTTP/1.1 400 Bad Request" }
        return { value = {codigo: "DADOS_INVALIDOS", mensagem: "Informe a situação do Procedimento."} }
      }
    }
    conditional {
      if (($bruto|get:"situacao"|is_text) == false || ($bruto.situacao != "ativo" && $bruto.situacao != "inativo")) {
        util.set_header { value = "HTTP/1.1 400 Bad Request" }
        return { value = {codigo: "DADOS_INVALIDOS", mensagem: "Informe situação ativo ou inativo."} }
      }
    }
    var $ativo { value = true }
    conditional {
      if ($bruto.situacao == "inativo") {
        var.update $ativo { value = false }
      }
    }
    db.edit procedimento {
      field_name = "id"
      field_value = $input.id
      data = {ativo: $ativo}
    } as $atualizado
  }
  response = {procedimento: {id: $atualizado.id, nome: $atualizado.nome, ativo: $atualizado.ativo}}
  history = false
  guid = "lxqFAbbvaTH8sOOeWzR3-n_quIg"
}
