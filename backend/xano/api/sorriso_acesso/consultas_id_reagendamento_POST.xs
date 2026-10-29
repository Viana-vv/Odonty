// Reagendamento administrativo: preserva a original e persiste vínculo explícito.
query "consultas/{id}/reagendamento" verb=POST {
  api_group = "Sorriso Acesso"
  auth = "conta_acesso"
  input { int id }
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
      output = ["id", "situacao", "perfis"]
    } as $solicitante
    conditional {
      if ($solicitante == null || $solicitante.situacao != "ativo" || ($solicitante.perfis|intersect:["administrador", "recepcionista"]|count) == 0) {
        util.set_header { value = "HTTP/1.1 403 Forbidden" }
        return { value = {codigo: "ACESSO_NEGADO", mensagem: "Reagendamento permitido somente à equipe administrativa autorizada."} }
      }
    }
    try_catch {
      try { util.get_raw_input { encoding = "json" } as $bruto }
      catch {
        util.set_header { value = "HTTP/1.1 400 Bad Request" }
        return { value = {codigo: "DADOS_INVALIDOS", mensagem: "Confira os dados do reagendamento."} }
      }
    }
    conditional {
      if (($bruto|is_object) == false || ($bruto|keys|count) != 2 || ($bruto|get:"disponibilidade_id"|is_int) == false || ($bruto|get:"justificativa"|is_text) == false) {
        util.set_header { value = "HTTP/1.1 400 Bad Request" }
        return { value = {codigo: "DADOS_INVALIDOS", mensagem: "Informe horário e justificativa do reagendamento."} }
      }
    }
    var $justificativa { value = $bruto.justificativa|trim }
    conditional {
      if ($input.id <= 0 || $bruto.disponibilidade_id <= 0 || ($justificativa|strlen) == 0 || ($justificativa|strlen) > 1000) {
        util.set_header { value = "HTTP/1.1 400 Bad Request" }
        return { value = {codigo: "DADOS_INVALIDOS", mensagem: "Informe identificadores válidos e uma justificativa de até 1000 caracteres."} }
      }
    }
    db.get consulta {
      field_name = "id"
      field_value = $input.id
      output = ["id", "paciente_id", "profissional_id", "inicio_em", "fim_em", "situacao"]
    } as $consulta
    db.get disponibilidade_agenda {
      field_name = "id"
      field_value = $bruto.disponibilidade_id
      output = ["id", "profissional_id", "inicio", "fim", "situacao"]
    } as $destino
    conditional {
      if ($consulta == null || $destino == null) {
        util.set_header { value = "HTTP/1.1 404 Not Found" }
        return { value = {codigo: "RECURSO_NAO_ENCONTRADO", mensagem: "Consulta ou horário não encontrado."} }
      }
    }
    db.query consulta_disponibilidade {
      where = $db.consulta_disponibilidade.consulta_id == $consulta.id
      return = {type: "single"}
      output = ["id", "disponibilidade_id"]
    } as $vinculo_original
    conditional {
      if (($consulta.situacao != "Agendada" && $consulta.situacao != "Confirmada") || $vinculo_original == null || $vinculo_original.disponibilidade_id == $destino.id) {
        util.set_header { value = "HTTP/1.1 409 Conflict" }
        return { value = {codigo: "REAGENDAMENTO_INVALIDO", mensagem: "Confira a situação da Consulta e escolha outro horário."} }
      }
    }
    var $profissionais { value = [$consulta.profissional_id] }
    conditional {
      if ($destino.profissional_id < $consulta.profissional_id) {
        var.update $profissionais { value = [$destino.profissional_id, $consulta.profissional_id] }
      }
      elseif ($destino.profissional_id > $consulta.profissional_id) {
        var.update $profissionais { value = [$consulta.profissional_id, $destino.profissional_id] }
      }
    }
    var $conflito { value = false }
    var $falha { value = false }
    var $nova_consulta { value = null }
    var $reagendamento { value = null }
    try_catch {
      try {
        db.transaction {
          stack {
            // Mesmas travas das rotas existentes, em ordem crescente de ID.
            foreach ($profissionais) {
              each as $profissional_id {
                db.query agenda_controle {
                  where = $db.agenda_controle.escopo == "profissional" && $db.agenda_controle.escopo_id == $profissional_id
                  return = {type: "single"}
                  output = ["id", "versao"]
                } as $controle_profissional
                conditional {
                  if ($controle_profissional == null) {
                    db.add agenda_controle {
                      data = {escopo: "profissional", escopo_id: $profissional_id, versao: 1, atualizado_em: now}
                    } as $controle_profissional_novo
                  }
                  else {
                    db.edit agenda_controle {
                      field_name = "id"
                      field_value = $controle_profissional.id
                      data = {versao: ($controle_profissional.versao + 1), atualizado_em: now}
                    } as $controle_profissional_editado
                  }
                }
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
                } as $controle_paciente_novo
              }
              else {
                db.edit agenda_controle {
                  field_name = "id"
                  field_value = $controle_paciente.id
                  data = {versao: ($controle_paciente.versao + 1), atualizado_em: now}
                } as $controle_paciente_editado
              }
            }
            db.get consulta {
              field_name = "id"
              field_value = $consulta.id
            } as $original_atual
            db.get paciente {
              field_name = "id"
              field_value = $consulta.paciente_id
              output = ["id", "situacao"]
            } as $paciente_atual
            db.get profissional {
              field_name = "id"
              field_value = $destino.profissional_id
              output = ["id", "situacao"]
            } as $profissional_atual
            db.get disponibilidade_agenda {
              field_name = "id"
              field_value = $destino.id
            } as $destino_atual
            db.get disponibilidade_agenda {
              field_name = "id"
              field_value = $vinculo_original.disponibilidade_id
            } as $origem_atual
            db.query consulta_disponibilidade {
              where = $db.consulta_disponibilidade.consulta_id == $consulta.id
              return = {type: "single"}
            } as $vinculo_atual
            db.query consulta_reagendamento {
              where = $db.consulta_reagendamento.consulta_original_id == $consulta.id
              return = {type: "single"}
            } as $reagendamento_existente
            db.query consulta {
              where = $db.consulta.id != $consulta.id && ($db.consulta.situacao == "Agendada" || $db.consulta.situacao == "Confirmada" || $db.consulta.situacao == "Em atendimento") && $db.consulta.inicio_em < $destino_atual.fim && $db.consulta.fim_em > $destino_atual.inicio && ($db.consulta.profissional_id == $destino.profissional_id || $db.consulta.paciente_id == $consulta.paciente_id)
              return = {type: "list"}
              output = ["id"]
            } as $conflitos_destino
            db.query consulta {
              where = $db.consulta.id != $consulta.id && ($db.consulta.situacao == "Agendada" || $db.consulta.situacao == "Confirmada" || $db.consulta.situacao == "Em atendimento") && $db.consulta.profissional_id == $consulta.profissional_id && $db.consulta.inicio_em < $consulta.fim_em && $db.consulta.fim_em > $consulta.inicio_em
              return = {type: "list"}
              output = ["id"]
            } as $conflitos_origem
            conditional {
              if ($original_atual == null || $original_atual.situacao != $consulta.situacao || $original_atual.paciente_id != $consulta.paciente_id || $original_atual.profissional_id != $consulta.profissional_id || $original_atual.inicio_em != $consulta.inicio_em || $original_atual.fim_em != $consulta.fim_em || $vinculo_atual == null || $vinculo_atual.disponibilidade_id != $vinculo_original.disponibilidade_id || $reagendamento_existente != null || $paciente_atual == null || $paciente_atual.situacao != "ativo" || $profissional_atual == null || $profissional_atual.situacao != "Ativo" || $destino_atual == null || $destino_atual.profissional_id != $destino.profissional_id || $destino_atual.situacao != "disponivel" || $destino_atual.inicio <= now || $destino_atual.fim <= $destino_atual.inicio || $origem_atual == null || $origem_atual.situacao != "reservado" || $origem_atual.profissional_id != $consulta.profissional_id || $origem_atual.inicio != $consulta.inicio_em || $origem_atual.fim != $consulta.fim_em || ($conflitos_destino|count) > 0 || ($conflitos_origem|count) > 0) {
                var.update $conflito { value = true }
              }
              else {
                db.add consulta {
                  data = {paciente_id: $consulta.paciente_id, profissional_id: $destino.profissional_id, procedimento_id: null, inicio_em: $destino_atual.inicio, fim_em: $destino_atual.fim, situacao: "Agendada", criado_em: now}
                } as $nova_consulta
                db.add consulta_disponibilidade {
                  data = {consulta_id: $nova_consulta.id, disponibilidade_id: $destino.id, criado_em: now}
                } as $novo_vinculo
                db.edit consulta {
                  field_name = "id"
                  field_value = $consulta.id
                  data = {situacao: "Cancelada"}
                } as $original_cancelada
                db.add consulta_situacao_historico {
                  data = {consulta_id: $consulta.id, situacao_anterior: $consulta.situacao, situacao_nova: "Cancelada", conta_acesso_id: $auth.id, motivo: $justificativa, alterado_em: now}
                } as $historico_original
                db.add consulta_situacao_historico {
                  data = {consulta_id: $nova_consulta.id, situacao_anterior: "Nova", situacao_nova: "Agendada", conta_acesso_id: $auth.id, motivo: $justificativa, alterado_em: now}
                } as $historico_novo
                db.add consulta_reagendamento {
                  data = {consulta_original_id: $consulta.id, consulta_nova_id: $nova_consulta.id, conta_acesso_id: $auth.id, justificativa: $justificativa, criado_em: now}
                } as $reagendamento
                conditional {
                  if ($origem_atual.inicio > now) {
                    db.edit disponibilidade_agenda {
                      field_name = "id"
                      field_value = $origem_atual.id
                      data = {situacao: "disponivel", atualizado_em: now}
                    } as $origem_liberada
                  }
                }
                db.edit disponibilidade_agenda {
                  field_name = "id"
                  field_value = $destino.id
                  data = {situacao: "reservado", atualizado_em: now}
                } as $destino_reservado
              }
            }
          }
        }
      }
      catch { var.update $falha { value = true } }
    }
    conditional {
      if ($conflito || $falha || $nova_consulta == null || $reagendamento == null) {
        util.set_header { value = "HTTP/1.1 409 Conflict" }
        return { value = {codigo: "CONFLITO_AGENDA", mensagem: "A Consulta ou o horário mudou. Confira a Agenda e tente novamente."} }
      }
    }
    util.set_header { value = "HTTP/1.1 201 Created" }
  }
  response = {consulta_original: {id: $consulta.id, paciente_id: $consulta.paciente_id, profissional_id: $consulta.profissional_id, disponibilidade_id: $vinculo_original.disponibilidade_id, situacao: "Cancelada"}, consulta: {id: $nova_consulta.id, paciente_id: $nova_consulta.paciente_id, profissional_id: $nova_consulta.profissional_id, disponibilidade_id: $destino.id, situacao: "Agendada"}, reagendamento_id: $reagendamento.id}
  history = false
  guid = "consultaReagendamentoPost64"
}
