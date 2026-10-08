// Agenda somente pela equipe administrativa; reserva e Consulta são atômicas.
query consultas verb=POST {
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
        return { value = {codigo: "ACESSO_NEGADO", mensagem: "Agendamento permitido somente à equipe administrativa autorizada."} }
      }
    }
    try_catch {
      try {
        util.get_raw_input { encoding = "json" } as $bruto
      }
      catch {
        util.set_header { value = "HTTP/1.1 400 Bad Request" }
        return { value = {codigo: "DADOS_INVALIDOS", mensagem: "Confira os dados da Consulta."} }
      }
    }
    var $campo_invalido { value = false }
    foreach ($bruto|keys) {
      each as $chave {
        conditional {
          if ($chave != "paciente_id" && $chave != "disponibilidade_id" && $chave != "procedimento_ids" && $chave != "motivo") {
            var.update $campo_invalido { value = true }
          }
        }
      }
    }
    conditional {
      if (($bruto|is_object) == false || $campo_invalido || ($bruto|keys|count) < 3 || ($bruto|keys|count) > 4 || ($bruto|get:"paciente_id"|is_int) == false || ($bruto|get:"disponibilidade_id"|is_int) == false || ($bruto|get:"procedimento_ids"|is_array) == false || (($bruto|get:"motivo") != null && ($bruto|get:"motivo"|is_text) == false)) {
        util.set_header { value = "HTTP/1.1 400 Bad Request" }
        return { value = {codigo: "DADOS_INVALIDOS", mensagem: "Confira os dados da Consulta."} }
      }
    }
    var $motivo { value = "" }
    conditional {
      if (($bruto|get:"motivo") != null) {
        var.update $motivo { value = $bruto.motivo|trim }
      }
    }
    var $procedimentos_invalidos { value = false }
    var $procedimentos_vistos { value = [] }
    foreach ($bruto.procedimento_ids) {
      each as $procedimento_id_validacao {
        conditional {
          if (($procedimento_id_validacao|is_int) == false || $procedimento_id_validacao <= 0) {
            var.update $procedimentos_invalidos { value = true }
          }
        }
        foreach ($procedimentos_vistos) {
          each as $procedimento_id_visto {
            conditional {
              if ($procedimento_id_visto == $procedimento_id_validacao) {
                var.update $procedimentos_invalidos { value = true }
              }
            }
          }
        }
        var.update $procedimentos_vistos {
          value = $procedimentos_vistos|push:$procedimento_id_validacao
        }
      }
    }
    conditional {
      if ($bruto.paciente_id <= 0 || $bruto.disponibilidade_id <= 0 || $procedimentos_invalidos || (($bruto|get:"motivo") != null && (($motivo|strlen) == 0 || ($motivo|strlen) > 1000))) {
        util.set_header { value = "HTTP/1.1 400 Bad Request" }
        return { value = {codigo: "DADOS_INVALIDOS", mensagem: "Confira os identificadores e o motivo informados."} }
      }
    }
    db.get paciente {
      field_name = "id"
      field_value = $bruto.paciente_id
      output = ["id", "situacao"]
    } as $paciente
    db.get disponibilidade_agenda {
      field_name = "id"
      field_value = $bruto.disponibilidade_id
      output = ["id", "profissional_id", "inicio", "fim", "situacao"]
    } as $disponibilidade
    conditional {
      if ($paciente == null || $paciente.situacao != "ativo" || $disponibilidade == null) {
        util.set_header { value = "HTTP/1.1 404 Not Found" }
        return { value = {codigo: "RECURSO_NAO_ENCONTRADO", mensagem: "Paciente ou horário não encontrado."} }
      }
      elseif ($disponibilidade.situacao != "disponivel" || $disponibilidade.inicio <= now) {
        util.set_header { value = "HTTP/1.1 409 Conflict" }
        return { value = {codigo: "CONFLITO_AGENDA", mensagem: "Este horário não está mais disponível."} }
      }
    }
    db.get profissional {
      field_name = "id"
      field_value = $disponibilidade.profissional_id
      output = ["id", "situacao", "agenda_lock_version"]
    } as $profissional
    conditional {
      if ($profissional == null || $profissional.situacao != "Ativo") {
        util.set_header { value = "HTTP/1.1 409 Conflict" }
        return { value = {codigo: "CONFLITO_AGENDA", mensagem: "Profissional indisponível para novos agendamentos."} }
      }
    }
    foreach ($bruto.procedimento_ids) {
      each as $procedimento_id {
        db.get procedimento {
          field_name = "id"
          field_value = $procedimento_id
          output = ["id", "ativo"]
        } as $procedimento
        conditional {
          if ($procedimento == null || $procedimento.ativo != true) {
            var.update $procedimentos_invalidos { value = true }
          }
        }
      }
    }
    conditional {
      if ($procedimentos_invalidos) {
        util.set_header { value = "HTTP/1.1 400 Bad Request" }
        return { value = {codigo: "DADOS_INVALIDOS", mensagem: "Há Procedimento inativo, inexistente ou duplicado."} }
      }
    }
    var $procedimento_legado { value = null }
    conditional {
      if (($bruto.procedimento_ids|count) > 0) {
        var.update $procedimento_legado { value = $bruto.procedimento_ids|get:0 }
      }
    }
    var $conflito { value = false }
    var $falha { value = false }
    var $nova_consulta { value = null }
    try_catch {
      try {
        db.transaction {
          stack {
            db.edit profissional {
              field_name = "id"
              field_value = $profissional.id
              data = {agenda_lock_version: ($profissional.agenda_lock_version + 1)}
            } as $trava_profissional
            // Incrementos dentro da transação serializam reservas para cada
            // Profissional e Paciente, inclusive solicitações concorrentes.
            db.query agenda_controle {
              where = $db.agenda_controle.escopo == "profissional" && $db.agenda_controle.escopo_id == $profissional.id
              return = {type: "single"}
              output = ["id", "versao"]
            } as $controle_profissional
            conditional {
              if ($controle_profissional == null) {
                db.add agenda_controle {
                  data = {escopo: "profissional", escopo_id: $profissional.id, versao: 1, atualizado_em: now}
                } as $novo_controle_profissional
              }
              else {
                db.edit agenda_controle {
                  field_name = "id"
                  field_value = $controle_profissional.id
                  data = {versao: ($controle_profissional.versao + 1), atualizado_em: now}
                } as $controle_profissional_atualizado
              }
            }
            db.query agenda_controle {
              where = $db.agenda_controle.escopo == "paciente" && $db.agenda_controle.escopo_id == $paciente.id
              return = {type: "single"}
              output = ["id", "versao"]
            } as $controle_paciente
            conditional {
              if ($controle_paciente == null) {
                db.add agenda_controle {
                  data = {escopo: "paciente", escopo_id: $paciente.id, versao: 1, atualizado_em: now}
                } as $novo_controle_paciente
              }
              else {
                db.edit agenda_controle {
                  field_name = "id"
                  field_value = $controle_paciente.id
                  data = {versao: ($controle_paciente.versao + 1), atualizado_em: now}
                } as $controle_paciente_atualizado
              }
            }
            db.get disponibilidade_agenda {
              field_name = "id"
              field_value = $disponibilidade.id
            } as $disponibilidade_bloqueada
            db.get profissional {
              field_name = "id"
              field_value = $profissional.id
              output = ["id", "situacao"]
            } as $profissional_bloqueado
            db.query consulta {
              where = ($db.consulta.situacao == "Agendada" || $db.consulta.situacao == "Confirmada" || $db.consulta.situacao == "Em atendimento") && $db.consulta.inicio_em < $disponibilidade.fim && $db.consulta.fim_em > $disponibilidade.inicio && ($db.consulta.profissional_id == $profissional.id || $db.consulta.paciente_id == $paciente.id)
              return = {type: "list"}
              output = ["id"]
            } as $consultas_conflitantes
            conditional {
              if ($profissional_bloqueado == null || $profissional_bloqueado.situacao != "Ativo" || $disponibilidade_bloqueada == null || $disponibilidade_bloqueada.situacao != "disponivel" || ($consultas_conflitantes|count) > 0) {
                var.update $conflito { value = true }
              }
              else {
                db.add consulta {
                  data = {paciente_id: $paciente.id, profissional_id: $profissional.id, procedimento_id: $procedimento_legado, inicio_em: $disponibilidade.inicio, fim_em: $disponibilidade.fim, situacao: "Agendada", observacoes: $motivo, criado_em: now}
                } as $nova_consulta
                db.add consulta_disponibilidade {
                  data = {consulta_id: $nova_consulta.id, disponibilidade_id: $disponibilidade.id, criado_em: now}
                } as $vinculo_disponibilidade
                foreach ($bruto.procedimento_ids) {
                  each as $procedimento_id {
                    db.add consulta_procedimento {
                      data = {consulta_id: $nova_consulta.id, procedimento_id: $procedimento_id, profissional_id: $profissional.id, criado_em: now}
                    } as $vinculo_procedimento
                  }
                }
                db.edit disponibilidade_agenda {
                  field_name = "id"
                  field_value = $disponibilidade.id
                  data = {situacao: "reservado", atualizado_em: now}
                } as $horario_reservado
                db.add consulta_situacao_historico {
                  data = {consulta_id: $nova_consulta.id, situacao_anterior: "Nova", situacao_nova: "Agendada", conta_acesso_id: $auth.id, motivo: $motivo, alterado_em: now}
                } as $historico_criacao
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
      if ($falha) {
        db.get disponibilidade_agenda {
          field_name = "id"
          field_value = $disponibilidade.id
          output = ["id", "situacao"]
        } as $disponibilidade_apos_falha
        db.query consulta {
          where = ($db.consulta.situacao == "Agendada" || $db.consulta.situacao == "Confirmada" || $db.consulta.situacao == "Em atendimento") && $db.consulta.inicio_em < $disponibilidade.fim && $db.consulta.fim_em > $disponibilidade.inicio && ($db.consulta.profissional_id == $profissional.id || $db.consulta.paciente_id == $paciente.id)
          return = {type: "list"}
          output = ["id"]
        } as $consultas_apos_falha
        conditional {
          if ($disponibilidade_apos_falha == null || $disponibilidade_apos_falha.situacao != "disponivel" || ($consultas_apos_falha|count) > 0) {
            var.update $conflito { value = true }
            var.update $falha { value = false }
          }
        }
      }
    }
    conditional {
      if ($conflito) {
        util.set_header { value = "HTTP/1.1 409 Conflict" }
        return { value = {codigo: "CONFLITO_AGENDA", mensagem: "Este horário conflita com outra Consulta ou foi reservado simultaneamente."} }
      }
      elseif ($falha || $nova_consulta == null) {
        util.set_header { value = "HTTP/1.1 503 Service Unavailable" }
        return { value = {codigo: "SERVICO_INDISPONIVEL", mensagem: "Não foi possível confirmar o agendamento."} }
      }
    }
    util.set_header { value = "HTTP/1.1 201 Created" }
  }
  response = {consulta: {id: $nova_consulta.id, paciente_id: $nova_consulta.paciente_id, profissional_id: $nova_consulta.profissional_id, disponibilidade_id: $bruto.disponibilidade_id, situacao: $nova_consulta.situacao}}
  history = false
  guid = "cRymQDMiqAXdp63TPPRMfX1IK9Y"
}
