// Marca um vínculo planejado como realizado sem alterar a autoria do planejamento.
query "consultas/{id}/procedimentos/{consulta_procedimento_id}/realizacao" verb=PATCH {
  api_group = "Sorriso Acesso"
  auth = "conta_acesso"
  input {
    int id
    int consulta_procedimento_id
  }
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
      if ($solicitante == null || $solicitante.situacao != "ativo" || ($solicitante.perfis|intersect:["profissional"]|count) == 0) {
        util.set_header { value = "HTTP/1.1 403 Forbidden" duplicates = "replace" }
        return { value = {codigo: "ACESSO_NEGADO", mensagem: "Conta sem permissão para realizar Procedimentos."} }
      }
    }
    db.get profissional {
      field_name = "conta_acesso_id"
      field_value = $auth.id
      output = ["id", "situacao"]
    } as $profissional_autenticado
    conditional {
      if ($profissional_autenticado == null || $profissional_autenticado.situacao != "Ativo") {
        util.set_header { value = "HTTP/1.1 403 Forbidden" duplicates = "replace" }
        return { value = {codigo: "ACESSO_NEGADO", mensagem: "Profissional sem acesso ativo."} }
      }
    }
    db.get consulta {
      field_name = "id"
      field_value = $input.id
      output = ["id", "profissional_id"]
    } as $consulta
    conditional {
      if ($consulta == null || $consulta.profissional_id != $profissional_autenticado.id) {
        util.set_header { value = "HTTP/1.1 404 Not Found" duplicates = "replace" }
        return { value = {codigo: "RECURSO_NAO_ENCONTRADO", mensagem: "Consulta não encontrada no escopo permitido."} }
      }
    }
    db.get consulta_procedimento {
      field_name = "id"
      field_value = $input.consulta_procedimento_id
      output = ["id", "consulta_id", "situacao", "profissional_id", "criado_em", "realizado_em", "realizado_por_profissional_id"]
    } as $vinculo
    conditional {
      if ($vinculo == null || $vinculo.consulta_id != $consulta.id) {
        util.set_header { value = "HTTP/1.1 404 Not Found" duplicates = "replace" }
        return { value = {codigo: "RECURSO_NAO_ENCONTRADO", mensagem: "Procedimento não encontrado no escopo permitido."} }
      }
    }
    conditional {
      if ($vinculo.situacao != "planejado") {
        util.set_header { value = "HTTP/1.1 409 Conflict" duplicates = "replace" }
        return { value = {codigo: "TRANSICAO_INVALIDA", mensagem: "Somente Procedimentos planejados podem ser realizados."} }
      }
    }
    var $atualizado { value = null }
    var $falha { value = false }
    try_catch {
      try {
        db.transaction {
          stack {
            db.get consulta_procedimento {
              field_name = "id"
              field_value = $vinculo.id
              output = ["id", "consulta_id", "situacao", "profissional_id", "criado_em", "realizado_em", "realizado_por_profissional_id"]
            } as $vinculo_atual
            conditional {
              if ($vinculo_atual == null || $vinculo_atual.consulta_id != $consulta.id || $vinculo_atual.situacao != "planejado") {
                var.update $falha { value = true }
              }
              else {
                db.edit consulta_procedimento {
                  field_name = "id"
                  field_value = $vinculo_atual.id
                  data = {situacao: "realizado", realizado_por_profissional_id: $profissional_autenticado.id, realizado_em: now}
                } as $atualizado
              }
            }
          }
        }
      }
      catch {
        var.update $falha { value = true }
      }
    }
    conditional {
      if ($falha || $atualizado == null) {
        util.set_header { value = "HTTP/1.1 409 Conflict" duplicates = "replace" }
        return { value = {codigo: "TRANSICAO_INVALIDA", mensagem: "O Procedimento mudou ou não foi possível confirmar a realização."} }
      }
    }
    var $realizado_em_iso { value = $atualizado.realizado_em|format_timestamp:"c":"UTC" }
    db.get profissional {
      field_name = "id"
      field_value = $atualizado.realizado_por_profissional_id
      output = ["id", "nome"]
    } as $responsavel
  }
  response = {procedimento: {id: $atualizado.id, consulta_id: $atualizado.consulta_id, situacao: $atualizado.situacao, profissional_id: $atualizado.profissional_id, criado_em: $atualizado.criado_em|format_timestamp:"c":"UTC", realizado_por_profissional_id: $atualizado.realizado_por_profissional_id, realizado_por_nome: $responsavel.nome, realizado_em: $realizado_em_iso}}
  history = false
}
