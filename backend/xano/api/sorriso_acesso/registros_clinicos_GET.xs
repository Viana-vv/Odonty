// Conteúdo clínico somente no endpoint dedicado e no escopo autorizado.
query "registros-clinicos" verb=GET {
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
    } as $solicitante
    conditional {
      if ($solicitante == null || $solicitante.situacao != "ativo" || ($solicitante.perfis|intersect:["profissional", "paciente"]|count) == 0) {
        util.set_header {
          value = "HTTP/1.1 403 Forbidden"
          duplicates = "replace"
        }
        return { value = {codigo: "ACESSO_NEGADO", mensagem: "Conta sem permissão para consultar conteúdo clínico."} }
      }
      elseif (($input.paciente_id != null && $input.paciente_id <= 0) || ($input.consulta_id != null && $input.consulta_id <= 0)) {
        util.set_header {
          value = "HTTP/1.1 400 Bad Request"
          duplicates = "replace"
        }
        return { value = {codigo: "DADOS_INVALIDOS", mensagem: "Confira os filtros informados."} }
      }
    }
    var $paciente_escopo { value = $input.paciente_id }
    var $profissional_escopo { value = null }
    conditional {
      if (($solicitante.perfis|intersect:["paciente"]|count) > 0) {
        db.get paciente {
          field_name = "conta_acesso_id"
          field_value = $auth.id
          output = ["id", "situacao"]
        } as $paciente_autenticado
        conditional {
          if ($paciente_autenticado == null || $paciente_autenticado.situacao != "ativo") {
            util.set_header {
              value = "HTTP/1.1 404 Not Found"
              duplicates = "replace"
            }
            return { value = {codigo: "RECURSO_NAO_ENCONTRADO", mensagem: "Conteúdo clínico não encontrado no escopo permitido."} }
          }
        }
        var.update $paciente_escopo { value = $paciente_autenticado.id }
      }
      else {
        db.get profissional {
          field_name = "conta_acesso_id"
          field_value = $auth.id
          output = ["id", "situacao"]
        } as $profissional_autenticado
        conditional {
          if ($profissional_autenticado == null || $profissional_autenticado.situacao != "Ativo") {
            util.set_header {
              value = "HTTP/1.1 403 Forbidden"
              duplicates = "replace"
            }
            return { value = {codigo: "ACESSO_NEGADO", mensagem: "Profissional sem permissão clínica ativa."} }
          }
        }
        var.update $profissional_escopo { value = $profissional_autenticado.id }
      }
    }
    // Consultar primeiro pelo escopo obrigatório evita filtros com OR/null
    // no db.query e impede carregar registros de outros Profissionais/Pacientes.
    var $registros_escopo { value = [] }
    conditional {
      if ($profissional_escopo != null) {
        db.query registro_clinico {
          where = $db.registro_clinico.profissional_id == $profissional_escopo
          sort = {registro_clinico.registrado_em: "desc", registro_clinico.id: "desc"}
          return = {type: "list"}
          output = ["id", "paciente_id", "profissional_id", "prontuario_id", "conteudo", "liberado_paciente", "consulta_id", "registrado_em"]
        } as $registros_profissional
        var.update $registros_escopo { value = $registros_profissional }
      }
      else {
        db.query registro_clinico {
          where = $db.registro_clinico.paciente_id == $paciente_escopo && $db.registro_clinico.liberado_paciente == true
          sort = {registro_clinico.registrado_em: "desc", registro_clinico.id: "desc"}
          return = {type: "list"}
          output = ["id", "paciente_id", "profissional_id", "prontuario_id", "conteudo", "liberado_paciente", "consulta_id", "registrado_em"]
        } as $registros_paciente
        var.update $registros_escopo { value = $registros_paciente }
      }
    }
    var $registros_clinicos { value = [] }
    foreach ($registros_escopo) {
      each as $registro {
        var $incluir_registro { value = true }
        conditional {
          if (($input.paciente_id != null && $registro.paciente_id != $input.paciente_id) || ($input.consulta_id != null && $registro.consulta_id != $input.consulta_id)) {
            var.update $incluir_registro { value = false }
          }
        }
        conditional {
          if ($incluir_registro) {
            db.query registro_clinico_retificacao {
              where = $db.registro_clinico_retificacao.registro_clinico_id == $registro.id
              sort = {registro_clinico_retificacao.criada_em: "asc", registro_clinico_retificacao.id: "asc"}
              return = {type: "list"}
              output = ["id", "profissional_id", "conteudo", "justificativa", "criada_em"]
            } as $retificacoes
            var $registro_formatado {
              value = {id: $registro.id, paciente_id: $registro.paciente_id, profissional_id: $registro.profissional_id, prontuario_id: $registro.prontuario_id, conteudo: $registro.conteudo, liberado_paciente: $registro.liberado_paciente, consulta_id: $registro.consulta_id, registrado_em: $registro.registrado_em, retificacoes: $retificacoes}
            }
            var.update $registros_clinicos {
              value = $registros_clinicos|push:$registro_formatado
            }
          }
        }
      }
    }
  }
  response = {registros_clinicos: $registros_clinicos}
  history = false
  guid = "5stj2LA3oijBKySyLKUSpK8UGKo"
}
