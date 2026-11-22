// Lista Exames no escopo do Profissional ou do Paciente autenticado.
query "exames" verb=GET {
  api_group = "Sorriso Acesso"
  auth = "conta_acesso"
  input {
    int paciente_id?
    int consulta_id?
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
    } as $conta
    conditional {
      if ($conta == null || $conta.situacao != "ativo" || ($conta.perfis|intersect:["profissional", "paciente", "recepcionista"]|count) == 0) {
        util.set_header { value = "HTTP/1.1 403 Forbidden" }
        return { value = {codigo: "ACESSO_NEGADO", mensagem: "Conta sem permissão para consultar Exames."} }
      }
    }
    var $exames { value = [] }
    conditional {
      if (($conta.perfis|intersect:["paciente"]|count) > 0) {
        db.get paciente {
          field_name = "conta_acesso_id"
          field_value = $auth.id
          output = ["id", "situacao"]
        } as $paciente_autenticado
        conditional {
          if ($paciente_autenticado == null || $paciente_autenticado.situacao != "ativo") {
            util.set_header { value = "HTTP/1.1 404 Not Found" }
            return { value = {codigo: "RECURSO_NAO_ENCONTRADO", mensagem: "Exames não encontrados no escopo permitido."} }
          }
        }
        conditional {
          if ($input.paciente_id > 0 && $input.paciente_id != $paciente_autenticado.id) {
            util.set_header { value = "HTTP/1.1 404 Not Found" }
            return { value = {codigo: "RECURSO_NAO_ENCONTRADO", mensagem: "Exames não encontrados no escopo permitido."} }
          }
        }
        db.query exame {
          where = $db.exame.paciente_id == $paciente_autenticado.id
          sort = {exame.solicitado_em: "desc"}
          return = {type: "list"}
          output = ["id", "paciente_id", "consulta_id", "tipo", "situacao", "solicitado_em", "realizado_em", "resultado"]
        } as $exames_paciente
        foreach ($exames_paciente) {
          each as $exame {
            var $incluir_exame { value = true }
            conditional {
              if ($input.consulta_id > 0 && $exame.consulta_id != $input.consulta_id) {
                var.update $incluir_exame { value = false }
              }
            }
            conditional {
              if ($incluir_exame) {
                var $resultado_liberado { value = null }
                conditional {
                  if ($exame.situacao == "Resultado disponível") {
                    var.update $resultado_liberado { value = $exame.resultado }
                  }
                }
                var $exame_paciente {
                  value = {id: $exame.id, paciente_id: $exame.paciente_id, consulta_id: $exame.consulta_id, tipo: $exame.tipo, situacao: $exame.situacao, solicitado_em: $exame.solicitado_em, realizado_em: $exame.realizado_em, resultado: $resultado_liberado}
                }
                var.update $exames { value = $exames|push:$exame_paciente }
              }
            }
          }
        }
      }
      elseif (($conta.perfis|intersect:["recepcionista"]|count) > 0) {
        db.query exame {
          sort = {exame.solicitado_em: "desc"}
          return = {type: "list"}
          output = ["id", "paciente_id", "consulta_id", "profissional_id", "tipo", "situacao", "solicitado_em", "realizado_em"]
        } as $exames_recepcao
        foreach ($exames_recepcao) {
          each as $exame {
            db.get paciente {
              field_name = "id"
              field_value = $exame.paciente_id
              output = ["id", "nome"]
            } as $paciente
            db.get consulta {
              field_name = "id"
              field_value = $exame.consulta_id
              output = ["id", "inicio_em"]
            } as $consulta
            db.get profissional {
              field_name = "id"
              field_value = $exame.profissional_id
              output = ["id", "nome"]
            } as $profissional
            var $exame_recepcao {
              value = {id: $exame.id, paciente_id: $exame.paciente_id, paciente_nome: $paciente.nome, consulta_id: $exame.consulta_id, consulta_inicio_em: $consulta.inicio_em, profissional_id: $exame.profissional_id, profissional_nome: $profissional.nome, tipo: $exame.tipo, situacao: $exame.situacao, solicitado_em: $exame.solicitado_em, realizado_em: $exame.realizado_em}
            }
            var.update $exames { value = $exames|push:$exame_recepcao }
          }
        }
      }
      else {
        db.get profissional {
          field_name = "conta_acesso_id"
          field_value = $auth.id
          output = ["id", "situacao"]
        } as $profissional
        conditional {
          if ($profissional == null || $profissional.situacao != "Ativo") {
            util.set_header { value = "HTTP/1.1 403 Forbidden" }
            return { value = {codigo: "ACESSO_NEGADO", mensagem: "Profissional sem permissão clínica ativa."} }
          }
        }
        db.query exame {
          where = $db.exame.profissional_id == $profissional.id
          sort = {exame.solicitado_em: "desc"}
          return = {type: "list"}
          output = ["id", "paciente_id", "consulta_id", "profissional_id", "tipo", "situacao", "solicitado_em", "realizado_em", "resultado", "observacoes"]
        } as $exames_profissional
        foreach ($exames_profissional) {
          each as $exame {
            var $incluir_exame { value = true }
            conditional {
              if (($input.paciente_id > 0 && $exame.paciente_id != $input.paciente_id) || ($input.consulta_id > 0 && $exame.consulta_id != $input.consulta_id)) {
                var.update $incluir_exame { value = false }
              }
            }
            conditional {
              if ($incluir_exame) {
                var $exame_profissional {
                  value = {id: $exame.id, paciente_id: $exame.paciente_id, consulta_id: $exame.consulta_id, profissional_id: $exame.profissional_id, tipo: $exame.tipo, situacao: $exame.situacao, solicitado_em: $exame.solicitado_em, realizado_em: $exame.realizado_em, resultado: $exame.resultado, observacoes: $exame.observacoes}
                }
                var.update $exames { value = $exames|push:$exame_profissional }
              }
            }
          }
        }
      }
    }
  }
  response = {exames: $exames}
  history = false
  guid = "LvZDzJY88ru6fWdYZhw4sSj0SX0"
}
