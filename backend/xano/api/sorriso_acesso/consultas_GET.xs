// Lista Consultas com escopo aplicado no Xano e dados administrativos mínimos.
query consultas verb=GET {
  api_group = "Sorriso Acesso"
  auth = "conta_acesso"
  input {
    int paciente_id?
    int profissional_id?
    text situacao?
    timestamp inicio?
    timestamp fim?
  }
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
      if ($solicitante == null || $solicitante.situacao != "ativo" || ($solicitante.perfis|intersect:["paciente", "profissional", "administrador", "recepcionista"]|count) == 0) {
        util.set_header { value = "HTTP/1.1 403 Forbidden" }
        return { value = {codigo: "ACESSO_NEGADO", mensagem: "Conta sem permissÃ£o para consultar Consultas."} }
      }
      elseif (($input.paciente_id != null && $input.paciente_id <= 0) || ($input.profissional_id != null && $input.profissional_id <= 0) || (($input.inicio == null) != ($input.fim == null)) || ($input.inicio != null && $input.fim <= $input.inicio) || ($input.situacao != null && $input.situacao != "Agendada" && $input.situacao != "Confirmada" && $input.situacao != "Em atendimento" && $input.situacao != "Realizada" && $input.situacao != "Cancelada" && $input.situacao != "Falta")) {
        util.set_header { value = "HTTP/1.1 400 Bad Request" }
        return { value = {codigo: "DADOS_INVALIDOS", mensagem: "Confira os filtros da Consulta."} }
      }
    }
    var $paciente_escopo { value = $input.paciente_id }
    var $profissional_escopo { value = null }
    var $situacao_armazenada { value = $input.situacao }
    conditional {
      if ($input.situacao == "Realizada") {
        var.update $situacao_armazenada { value = "ConcluÃ­da" }
      }
    }
    conditional {
      if (($solicitante.perfis|intersect:["paciente"]|count) > 0) {
        db.get paciente {
          field_name = "conta_acesso_id"
          field_value = $auth.id
          output = ["id", "situacao"]
        } as $paciente_autenticado
        conditional {
          if ($paciente_autenticado == null || $paciente_autenticado.situacao != "ativo") {
            util.set_header { value = "HTTP/1.1 404 Not Found" }
            return { value = {codigo: "RECURSO_NAO_ENCONTRADO", mensagem: "Consultas nÃ£o encontradas no escopo permitido."} }
          }
        }
        var.update $paciente_escopo { value = $paciente_autenticado.id }
      }
      elseif (($solicitante.perfis|intersect:["profissional"]|count) > 0) {
        db.get profissional {
          field_name = "conta_acesso_id"
          field_value = $auth.id
          output = ["id", "situacao"]
        } as $profissional_autenticado
        conditional {
          if ($profissional_autenticado == null || $profissional_autenticado.situacao != "Ativo") {
            util.set_header { value = "HTTP/1.1 403 Forbidden" }
            return { value = {codigo: "ACESSO_NEGADO", mensagem: "Profissional sem acesso Ã  Agenda."} }
          }
        }
        var.update $profissional_escopo { value = $profissional_autenticado.id }
      }
    }
    // Filtros opcionais são aplicados após a consulta base. No Xano,
    // as condições de null no where omitiram registros existentes.
    db.query consulta {
      sort = {consulta.inicio_em: "asc", consulta.id: "asc"}
      return = {type: "list"}
      output = ["id", "paciente_id", "profissional_id", "procedimento_id", "inicio_em", "fim_em", "situacao"]
    } as $consultas
    var $consultas_formatadas { value = [] }
    foreach ($consultas) {
      each as $consulta {
        var $incluir_consulta { value = true }
        conditional {
          if (($paciente_escopo != null && $consulta.paciente_id != $paciente_escopo) || ($profissional_escopo != null && $consulta.profissional_id != $profissional_escopo) || ($input.paciente_id != null && $consulta.paciente_id != $input.paciente_id) || ($input.profissional_id != null && $consulta.profissional_id != $input.profissional_id) || ($input.situacao != null && $consulta.situacao != $situacao_armazenada) || ($input.inicio != null && ($consulta.inicio_em < $input.inicio || $consulta.fim_em > $input.fim))) {
            var.update $incluir_consulta { value = false }
          }
        }
        conditional {
          if ($incluir_consulta) {
        var $inicio_iso { value = $consulta.inicio_em|format_timestamp:"c":"UTC" }
        var $fim_iso { value = $consulta.fim_em|format_timestamp:"c":"UTC" }
        db.get paciente {
          field_name = "id"
          field_value = $consulta.paciente_id
          output = ["id", "nome"]
        } as $paciente
        db.get profissional {
          field_name = "id"
          field_value = $consulta.profissional_id
          output = ["id", "nome"]
        } as $profissional
        db.get consulta_disponibilidade {
          field_name = "consulta_id"
          field_value = $consulta.id
          output = ["disponibilidade_id"]
        } as $vinculo_disponibilidade
        var $disponibilidade_id { value = null }
        conditional {
          if ($vinculo_disponibilidade != null) {
            var.update $disponibilidade_id { value = $vinculo_disponibilidade.disponibilidade_id }
          }
        }
        var $procedimento_nome { value = null }
        conditional {
          if ($consulta.procedimento_id != null) {
            db.get procedimento {
              field_name = "id"
              field_value = $consulta.procedimento_id
              output = ["id", "nome"]
            } as $procedimento_legado
            conditional {
              if ($procedimento_legado != null) {
                var.update $procedimento_nome { value = $procedimento_legado.nome }
              }
            }
          }
        }
        db.query consulta_procedimento {
          where = $db.consulta_procedimento.consulta_id == $consulta.id
          return = {type: "list"}
          output = ["procedimento_id"]
        } as $procedimentos_vinculados
        conditional {
          if (($procedimentos_vinculados|count) > 0) {
            foreach ($procedimentos_vinculados) {
              each as $vinculo_procedimento {
                db.get procedimento {
                  field_name = "id"
                  field_value = $vinculo_procedimento.procedimento_id
                  output = ["id", "nome"]
                } as $procedimento_vinculado
                var $procedimento_vinculado_nome { value = null }
                conditional {
                  if ($procedimento_vinculado != null) {
                    var.update $procedimento_vinculado_nome { value = $procedimento_vinculado.nome }
                  }
                }
                var $consulta_formatada {
                  value = {id: $consulta.id, paciente_id: $consulta.paciente_id, profissional_id: $consulta.profissional_id, inicio_em: $inicio_iso, fim_em: $fim_iso, situacao: $consulta.situacao, disponibilidade_id: $disponibilidade_id, paciente_nome: $paciente.nome, profissional_nome: $profissional.nome, procedimento_nome: $procedimento_nome, procedimento_vinculado_nome: $procedimento_vinculado_nome}
                }
                var.update $consultas_formatadas {
                  value = $consultas_formatadas|push:$consulta_formatada
                }
              }
            }
          }
          else {
            var $consulta_formatada {
              value = {id: $consulta.id, paciente_id: $consulta.paciente_id, profissional_id: $consulta.profissional_id, inicio_em: $inicio_iso, fim_em: $fim_iso, situacao: $consulta.situacao, disponibilidade_id: $disponibilidade_id, paciente_nome: $paciente.nome, profissional_nome: $profissional.nome, procedimento_nome: $procedimento_nome, procedimento_vinculado_nome: null}
            }
            var.update $consultas_formatadas {
              value = $consultas_formatadas|push:$consulta_formatada
            }
          }
        }
          }
        }
      }
    }
  }
  response = {consultas: $consultas_formatadas}
  history = false
  guid = "p107TSKMEOjzrvK2A7U3vHSa5Q8"
}
