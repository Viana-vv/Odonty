// Edita o catÃ¡logo ou altera a situaÃ§Ã£o sem remover histÃ³rico.
query "procedimentos/{id}" verb=PATCH {
  api_group = "Sorriso Acesso"
  auth = "conta_acesso"
  input { int id }
  stack {
    util.set_header { value = "Cache-Control: no-store" duplicates = "replace" }
    function.run sorriso_validar_sessao { input = {conta_id: $auth.id, sessao_id: $auth.extras.sessao_id} } as $sessao
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
        return { value = {codigo: "DADOS_INVALIDOS", mensagem: "Informe uma alteração válida."} }
      }
    }
    conditional {
      if (($bruto|get:"nome") != null) {
        conditional {
          if (($bruto.nome|is_text) == false || (($bruto.nome|trim)|strlen) < 2 || (($bruto.nome|trim)|strlen) > 120) {
            util.set_header { value = "HTTP/1.1 400 Bad Request" }
            return { value = {codigo: "DADOS_INVALIDOS", mensagem: "Informe um nome de Procedimento entre 2 e 120 caracteres."} }
          }
        }
      }
    }
    conditional {
      if (($bruto|get:"ativo") != null) {
        conditional {
          if (($bruto.ativo|is_bool) == false) {
            util.set_header { value = "HTTP/1.1 400 Bad Request" }
            return { value = {codigo: "DADOS_INVALIDOS", mensagem: "Informe uma situação válida."} }
          }
        }
      }
    }
    conditional {
      if (($bruto|get:"nome") == null && ($bruto|get:"ativo") == null) {
        util.set_header { value = "HTTP/1.1 400 Bad Request" }
        return { value = {codigo: "DADOS_INVALIDOS", mensagem: "Informe uma alteração."} }
      }
    }
    conditional {
      if (($bruto|get:"nome") != null && ($bruto|get:"ativo") != null) {
        db.edit procedimento {
          field_name = "id"
          field_value = $input.id
          data = {nome: ($bruto.nome|trim), ativo: $bruto.ativo}
        } as $atualizado
      }
      elseif (($bruto|get:"nome") != null) {
        db.edit procedimento {
          field_name = "id"
          field_value = $input.id
          data = {nome: ($bruto.nome|trim)}
        } as $atualizado
      }
      else {
        db.edit procedimento {
          field_name = "id"
          field_value = $input.id
          data = {ativo: $bruto.ativo}
        } as $atualizado
      }
    }
  }
  response = {procedimento: {id: $atualizado.id, nome: $atualizado.nome, ativo: $atualizado.ativo}}
  history = false
  guid = "LSXvO3ZIhRt2iy2167opdm4AaMI"
}
