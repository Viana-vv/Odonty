// Conteúdo clínico somente no endpoint dedicado e no escopo autorizado.
query "registros-clinicos" verb=GET {
  api_group = "Sorriso Acesso"
  auth = "conta_acesso"
  input {
    int paciente_id?
    int consulta_id?
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
      if ($solicitante == null || $solicitante.situacao != "ativo" || ($solicitante.perfis|intersect:["profissional", "paciente"]|count) == 0) {
        util.set_header { value = "HTTP/1.1 403 Forbidden" }
        return { value = {codigo: "ACESSO_NEGADO", mensagem: "Conta sem permissão para consultar conteúdo clínico."} }
      }
      elseif (($input.paciente_id != null && $input.paciente_id <= 0) || ($input.consulta_id != null && $input.consulta_id <= 0)) {
        util.set_header { value = "HTTP/1.1 400 Bad Request" }
        return { value = {codigo: "DADOS_INVALIDOS", mensagem: "Confira os filtros informados."} }
      }
    }
    var $paciente_escopo { value = $input.paciente_id }
    var $profissional_escopo { value = null }
    conditional {
      if (($solicitante.perfis|includes:"paciente")) {
        db.get paciente {
          field_name = "conta_acesso_id"
          field_value = $auth.id
          output = ["id", "situacao"]
        } as $paciente_autenticado
        conditional {
          if ($paciente_autenticado == null || $paciente_autenticado.situacao != "ativo") {
            util.set_header { value = "HTTP/1.1 404 Not Found" }
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
            util.set_header { value = "HTTP/1.1 403 Forbidden" }
            return { value = {codigo: "ACESSO_NEGADO", mensagem: "Profissional sem permissão clínica ativa."} }
          }
        }
        var.update $profissional_escopo { value = $profissional_autenticado.id }
      }
    }
    db.query registro_clinico {
      where = ($paciente_escopo == null || $db.registro_clinico.paciente_id == $paciente_escopo) && ($input.consulta_id == null || $db.registro_clinico.consulta_id == $input.consulta_id) && (($solicitante.perfis|includes:"paciente") == false || $db.registro_clinico.liberado_paciente == true) && ($profissional_escopo == null || $db.registro_clinico.profissional_id == $profissional_escopo)
      sort = {registro_clinico.registrado_em: "desc", registro_clinico.id: "desc"}
      return = {type: "list"}
      output = ["id", "paciente_id", "profissional_id", "prontuario_id", "conteudo", "liberado_paciente", "consulta_id", "registrado_em"]
    } as $registros_clinicos
  }
  response = {registros_clinicos: $registros_clinicos}
  history = false
}
