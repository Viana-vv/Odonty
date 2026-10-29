query "exames/{exame_id}/situacao" verb=PATCH {
  api_group = "Sorriso Acesso"
  auth = "conta_acesso"
  input {
    int exame_id
    enum situacao {
      values = ["Realizado", "Resultado disponível", "Cancelado", "Não realizado"]
    }
    text resultado?
    timestamp realizado_em?
    text observacoes?
  }
  stack {
    function.run sorriso_validar_sessao {
      input = {conta_id: $auth.id, sessao_id: $auth.extras.sessao_id}
    } as $sessao
    db.get conta_acesso {
      field_name = "id"
      field_value = $auth.id
      output = ["id", "perfis", "situacao"]
    } as $conta
    db.get profissional {
      field_name = "conta_acesso_id"
      field_value = $auth.id
      output = ["id", "situacao"]
    } as $profissional
    db.get exame {
      field_name = "id"
      field_value = $input.exame_id
      output = ["id", "profissional_id", "situacao", "solicitado_em", "realizado_em", "resultado", "observacoes"]
    } as $exame
    conditional {
      if ($conta == null || $conta.situacao != "ativo" || ($conta.perfis|intersect:["profissional"]|count) == 0 || $profissional == null || $profissional.situacao != "Ativo") {
        util.set_header { value = "HTTP/1.1 403 Forbidden" }
        return { value = {codigo: "ACESSO_NEGADO", mensagem: "Somente Profissional autorizado pode atualizar Exames."} }
      }
    }
    conditional {
      if ($exame == null || $exame.profissional_id != $profissional.id) {
        util.set_header { value = "HTTP/1.1 404 Not Found" }
        return { value = {codigo: "RECURSO_NAO_ENCONTRADO", mensagem: "Exame não encontrado no escopo permitido."} }
      }
    }
    var $transicao_permitida { value = false }
    conditional {
      if ($exame.situacao == "Solicitado" && ($input.situacao == "Realizado" || $input.situacao == "Cancelado" || $input.situacao == "Não realizado")) {
        var.update $transicao_permitida { value = true }
      }
      elseif ($exame.situacao == "Realizado" && $input.situacao == "Resultado disponível") {
        var.update $transicao_permitida { value = true }
      }
    }
    conditional {
      if ($transicao_permitida == false) {
        util.set_header { value = "HTTP/1.1 409 Conflict" }
        return { value = {codigo: "TRANSICAO_INVALIDA", mensagem: "A situação atual do Exame não permite essa alteração."} }
      }
    }
    var $realizado_em_final { value = $exame.realizado_em }
    conditional {
      if ($input.realizado_em != null) {
        var.update $realizado_em_final { value = $input.realizado_em }
      }
    }
    var $resultado_final { value = $exame.resultado }
    conditional {
      if ($input.resultado != null) {
        var.update $resultado_final { value = $input.resultado }
      }
    }
    var $observacoes_finais { value = $exame.observacoes }
    conditional {
      if ($input.observacoes != null) {
        var.update $observacoes_finais { value = $input.observacoes }
      }
    }
    conditional {
      if (($input.situacao == "Realizado" || $input.situacao == "Resultado disponível") && ($realizado_em_final == null || $realizado_em_final < $exame.solicitado_em || $realizado_em_final > now)) {
        util.set_header { value = "HTTP/1.1 400 Bad Request" }
        return { value = {codigo: "DATA_INVALIDA", mensagem: "A data da realização deve ser posterior à solicitação e não pode estar no futuro."} }
      }
      elseif ($input.situacao == "Resultado disponível" && ($resultado_final == null || ($resultado_final|trim) == "")) {
        util.set_header { value = "HTTP/1.1 400 Bad Request" }
        return { value = {codigo: "RESULTADO_OBRIGATORIO", mensagem: "Informe o resultado antes de disponibilizá-lo ao Paciente."} }
      }
    }
    var $conflito { value = false }
    var $falha_transacao { value = false }
    var $atualizado { value = null }
    try_catch {
      try {
        db.transaction {
          stack {
            db.get exame_situacao_controle {
              field_name = "exame_id"
              field_value = $exame.id
              output = ["id", "versao"]
            } as $controle_situacao
            conditional {
              if ($controle_situacao == null) {
                var.update $falha_transacao { value = true }
              }
              else {
                db.edit exame_situacao_controle {
                  field_name = "id"
                  field_value = $controle_situacao.id
                  data = {versao: ($controle_situacao.versao + 1), atualizado_em: now}
                } as $trava_situacao
                db.get exame {
                  field_name = "id"
                  field_value = $exame.id
                  output = ["id", "profissional_id", "situacao"]
                } as $exame_atual
                conditional {
                  if ($exame_atual == null || $exame_atual.profissional_id != $profissional.id || $exame_atual.situacao != $exame.situacao) {
                    var.update $conflito { value = true }
                  }
                  else {
                    db.edit exame {
                      field_name = "id"
                      field_value = $exame.id
                      data = {situacao: $input.situacao, resultado: $resultado_final, realizado_em: $realizado_em_final, observacoes: $observacoes_finais}
                    } as $atualizado
                    db.add exame_situacao_historico {
                      data = {exame_id: $exame.id, situacao_anterior: $exame_atual.situacao, situacao_nova: $input.situacao, conta_acesso_id: $auth.id, alterado_em: now}
                    } as $historico
                  }
                }
              }
            }
          }
        }
      }
      catch {
        var.update $falha_transacao { value = true }
      }
    }
    conditional {
      if ($falha_transacao) {
        util.set_header { value = "HTTP/1.1 503 Service Unavailable" }
        return { value = {codigo: "SERVICO_INDISPONIVEL", mensagem: "Não foi possível atualizar o Exame. Tente novamente."} }
      }
      elseif ($conflito) {
        util.set_header { value = "HTTP/1.1 409 Conflict" }
        return { value = {codigo: "CONFLITO_EXAME", mensagem: "O Exame foi atualizado por outra operação. Atualize a lista e tente novamente."} }
      }
    }
  }
  response = {exame: $atualizado}
  history = false
}
