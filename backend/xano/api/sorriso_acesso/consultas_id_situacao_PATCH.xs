// Aplica transição permitida, registra auditoria e libera horário ao cancelar.
query "consultas/{id}/situacao" verb=PATCH {
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
      if ($solicitante == null || $solicitante.situacao != "ativo" || ($solicitante.perfis|intersect:["profissional", "administrador", "recepcionista"]|count) == 0) {
        util.set_header { value = "HTTP/1.1 403 Forbidden" }
        return { value = {codigo: "ACESSO_NEGADO", mensagem: "Conta sem permissão para atualizar Consultas."} }
      }
    }
    try_catch {
      try {
        util.get_raw_input { encoding = "json" } as $bruto
      }
      catch {
        util.set_header { value = "HTTP/1.1 400 Bad Request" }
        return { value = {codigo: "DADOS_INVALIDOS", mensagem: "Confira a atualização da Consulta."} }
      }
    }
    var $campo_invalido { value = false }
    foreach ($bruto|keys) {
      each as $chave {
        conditional {
          if ($chave not in ["situacao", "motivo_cancelamento"]) {
            var.update $campo_invalido { value = true }
          }
        }
      }
    }
    conditional {
      if (($bruto|is_object) == false || $campo_invalido || ($bruto|keys|count) < 1 || ($bruto|keys|count) > 2 || ($bruto|get:"situacao"|is_text) == false || (($bruto|get:"motivo_cancelamento") != null && ($bruto|get:"motivo_cancelamento"|is_text) == false) || ($bruto.situacao not in ["Agendada", "Confirmada", "Em atendimento", "Realizada", "Cancelada", "Falta"]) || ($bruto.situacao == "Cancelada" && (($bruto|get:"motivo_cancelamento") == null || (($bruto.motivo_cancelamento|trim)|strlen) == 0 || (($bruto.motivo_cancelamento|trim)|strlen) > 1000))) {
        util.set_header { value = "HTTP/1.1 400 Bad Request" }
        return { value = {codigo: "DADOS_INVALIDOS", mensagem: "Informe situação válida e motivo para cancelamento."} }
      }
    }
    db.get consulta {
      field_name = "id"
      field_value = $input.id
      output = ["id", "paciente_id", "profissional_id", "inicio_em", "fim_em", "situacao"]
    } as $consulta
    conditional {
      if ($consulta == null) {
        util.set_header { value = "HTTP/1.1 404 Not Found" }
        return { value = {codigo: "RECURSO_NAO_ENCONTRADO", mensagem: "Consulta não encontrada no escopo permitido."} }
      }
    }
    var $profissional_escopo { value = null }
    conditional {
      if (($solicitante.perfis|includes:"profissional")) {
        db.get profissional {
          field_name = "conta_acesso_id"
          field_value = $auth.id
          output = ["id", "situacao"]
        } as $profissional_autenticado
        conditional {
          if ($profissional_autenticado == null || $profissional_autenticado.situacao != "Ativo" || $profissional_autenticado.id != $consulta.profissional_id) {
            util.set_header { value = "HTTP/1.1 404 Not Found" }
            return { value = {codigo: "RECURSO_NAO_ENCONTRADO", mensagem: "Consulta não encontrada no escopo permitido."} }
          }
        }
        var.update $profissional_escopo { value = $profissional_autenticado.id }
      }
    }
    var $situacao_atual { value = $consulta.situacao }
    var $situacao_nova { value = $bruto.situacao }
    var $motivo { value = ($bruto|get:"motivo_cancelamento"|default:"")|trim }
    conditional {
      if ($situacao_atual == "Concluída") {
        var.update $situacao_atual { value = "Realizada" }
      }
      if ($situacao_nova == "Realizada") {
        var.update $situacao_nova { value = "Concluída" }
      }
    }
    conditional {
      if (($situacao_atual == "Agendada" && $bruto.situacao not in ["Confirmada", "Cancelada"]) || ($situacao_atual == "Confirmada" && $bruto.situacao not in ["Em atendimento", "Cancelada", "Falta"]) || ($situacao_atual == "Em atendimento" && $bruto.situacao != "Realizada") || ($situacao_atual not in ["Agendada", "Confirmada", "Em atendimento"]) || (($bruto.situacao in ["Em atendimento", "Realizada", "Falta"]) && ($solicitante.perfis|includes:"profissional") == false)) {
        util.set_header { value = "HTTP/1.1 409 Conflict" }
        return { value = {codigo: "TRANSICAO_INVALIDA", mensagem: "A transição da Consulta não é permitida para esta Conta de Acesso."} }
      }
    }
    db.query consulta_disponibilidade {
      where = $db.consulta_disponibilidade.consulta_id == $consulta.id
      return = {type: "single"}
      output = ["id", "disponibilidade_id"]
    } as $vinculo
    var $disponibilidade_id { value = null }
    conditional {
      if ($vinculo != null) {
        var.update $disponibilidade_id { value = $vinculo.disponibilidade_id }
      }
    }
    var $consulta_atualizada { value = null }
    var $falha { value = false }
    try_catch {
      try {
        db.transaction {
          stack {
            db.query agenda_controle {
              where = $db.agenda_controle.escopo == "profissional" && $db.agenda_controle.escopo_id == $consulta.profissional_id
              return = {type: "single"}
              output = ["id", "versao"]
            } as $controle_profissional
            conditional {
              if ($controle_profissional == null) {
                db.add agenda_controle {
                  data = {escopo: "profissional", escopo_id: $consulta.profissional_id, versao: 1, atualizado_em: now}
                } as $novo_controle_profissional
              }
              else {
                db.edit agenda_controle {
                  field_name = "id"
                  field_value = $controle_profissional.id
                  data = {versao: (($controle_profissional.versao|default:0) + 1), atualizado_em: now}
                } as $controle_profissional_atualizado
              }
            }
            db.query agenda_controle {
              where = $db.agenda_controle.escopo == "paciente" && $db.agenda_controle.escopo_id == $consulta.paciente_id
              return = {type: "single"}
              output = ["id", "versao"]
            } as $controle_paciente
            conditional {
              if ($controle_paciente == null) {
                db.add agenda_controle {
                  data = {escopo: "paciente", escopo_id: $consulta.paciente_id, versao: 1, atualizado_em: now}
                } as $novo_controle_paciente
              }
              else {
                db.edit agenda_controle {
                  field_name = "id"
                  field_value = $controle_paciente.id
                  data = {versao: (($controle_paciente.versao|default:0) + 1), atualizado_em: now}
                } as $controle_paciente_atualizado
              }
            }
            db.query consulta {
              where = $db.consulta.id == $consulta.id
              return = {type: "single"}
              output = ["id", "situacao"]
            } as $situacao_concorrente
            conditional {
              if ($situacao_concorrente.situacao != $consulta.situacao) {
                var.update $falha { value = true }
              }
              else {
                db.edit consulta {
                  field_name = "id"
                  field_value = $consulta.id
                  data = {situacao: $situacao_nova}
                } as $consulta_atualizada
                db.add consulta_situacao_historico {
                  data = {consulta_id: $consulta.id, situacao_anterior: $situacao_atual, situacao_nova: $bruto.situacao, conta_acesso_id: $auth.id, motivo: $motivo, alterado_em: now}
                } as $historico
                conditional {
                  if ($bruto.situacao == "Cancelada" && $vinculo != null) {
                    db.get disponibilidade_agenda {
                      field_name = "id"
                      field_value = $vinculo.disponibilidade_id
                    } as $disponibilidade
                    conditional {
                      if ($disponibilidade != null && $disponibilidade.inicio > now) {
                        db.edit disponibilidade_agenda {
                          field_name = "id"
                          field_value = $disponibilidade.id
                          data = {situacao: "disponivel", atualizado_em: now}
                        } as $horario_liberado
                      }
                    }
                  }
                }
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
      if ($falha || $consulta_atualizada == null) {
        util.set_header { value = "HTTP/1.1 409 Conflict" }
        return { value = {codigo: "CONFLITO_AGENDA", mensagem: "A Consulta mudou ou não foi possível concluir a atualização."} }
      }
    }
    var $situacao_resposta { value = $consulta_atualizada.situacao }
    conditional {
      if ($situacao_resposta == "Concluída") {
        var.update $situacao_resposta { value = "Realizada" }
      }
    }
  }
  response = {consulta: {id: $consulta_atualizada.id, paciente_id: $consulta_atualizada.paciente_id, profissional_id: $consulta_atualizada.profissional_id, disponibilidade_id: $disponibilidade_id, situacao: $situacao_resposta}}
  history = false
}
