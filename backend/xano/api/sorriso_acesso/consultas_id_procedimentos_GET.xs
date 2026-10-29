// Lista Procedimentos da Consulta somente para o Profissional responsável.
query "consultas/{id}/procedimentos" verb=GET {
  api_group = "Sorriso Acesso"
  auth = "conta_acesso"
  input {
    int id
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
        util.set_header { value = "HTTP/1.1 403 Forbidden" }
        return { value = {codigo: "ACESSO_NEGADO", mensagem: "Conta sem permissão para consultar Procedimentos."} }
      }
    }
    db.get profissional {
      field_name = "conta_acesso_id"
      field_value = $auth.id
      output = ["id", "situacao"]
    } as $profissional_autenticado
    conditional {
      if ($profissional_autenticado == null || $profissional_autenticado.situacao != "Ativo") {
        util.set_header { value = "HTTP/1.1 403 Forbidden" }
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
        util.set_header { value = "HTTP/1.1 404 Not Found" }
        return { value = {codigo: "RECURSO_NAO_ENCONTRADO", mensagem: "Consulta não encontrada no escopo permitido."} }
      }
    }
    db.query consulta_procedimento {
      where = $db.consulta_procedimento.consulta_id == $consulta.id
      sort = {consulta_procedimento.id: "asc"}
      return = {type: "list"}
      output = ["id", "consulta_id", "procedimento_id", "profissional_id", "criado_em", "situacao", "realizado_por_profissional_id", "realizado_em"]
    } as $vinculos
    var $itens { value = [] }
    foreach ($vinculos) {
      each as $vinculo {
        db.get procedimento {
          field_name = "id"
          field_value = $vinculo.procedimento_id
          output = ["id", "nome"]
        } as $procedimento
        var $profissional_planejamento_nome { value = null }
        conditional {
          if ($vinculo.profissional_id != null) {
            db.get profissional {
              field_name = "id"
              field_value = $vinculo.profissional_id
              output = ["id", "nome"]
            } as $profissional_planejamento
            conditional {
              if ($profissional_planejamento != null) {
                var.update $profissional_planejamento_nome { value = $profissional_planejamento.nome }
              }
            }
          }
        }
        var $realizado_em_iso { value = null }
        var $realizado_por_nome { value = null }
        conditional {
          if ($vinculo.realizado_em != null) {
            var.update $realizado_em_iso { value = $vinculo.realizado_em|format_timestamp:"c":"UTC" }
          }
        }
        conditional {
          if ($vinculo.realizado_por_profissional_id != null) {
            db.get profissional {
              field_name = "id"
              field_value = $vinculo.realizado_por_profissional_id
              output = ["id", "nome"]
            } as $profissional_realizador
            conditional {
              if ($profissional_realizador != null) {
                var.update $realizado_por_nome { value = $profissional_realizador.nome }
              }
            }
          }
        }
        var $criado_em_iso { value = null }
        conditional {
          if ($vinculo.criado_em != null) {
            var.update $criado_em_iso { value = $vinculo.criado_em|format_timestamp:"c":"UTC" }
          }
        }
        var $item {
          value = {id: $vinculo.id, consulta_id: $vinculo.consulta_id, procedimento_id: $vinculo.procedimento_id, procedimento_nome: $procedimento.nome, situacao: $vinculo.situacao, profissional_id: $vinculo.profissional_id, profissional_planejamento_nome: $profissional_planejamento_nome, criado_em: $criado_em_iso, realizado_por_profissional_id: $vinculo.realizado_por_profissional_id, realizado_por_nome: $realizado_por_nome, realizado_em: $realizado_em_iso}
        }
        var.update $itens { value = $itens|push:$item }
      }
    }
  }
  response = {procedimentos: $itens}
  history = false
}
