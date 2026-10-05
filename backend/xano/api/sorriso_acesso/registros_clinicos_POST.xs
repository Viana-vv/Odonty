// Cria Registro Clínico somente por Profissional ativo e autorizado.
query "registros-clinicos" verb=POST {
  api_group = "Sorriso Acesso"
  auth = "conta_acesso"
  input { }
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
      if ($solicitante == null || $solicitante.situacao != "ativo" || ($solicitante.perfis|includes:"profissional") == false) {
        util.set_header { value = "HTTP/1.1 403 Forbidden" }
        return { value = {codigo: "ACESSO_NEGADO", mensagem: "Registro Clínico permitido somente a Profissional autorizado."} }
      }
    }
    try_catch {
      try {
        util.get_raw_input { encoding = "json" } as $bruto
      }
      catch {
        util.set_header { value = "HTTP/1.1 400 Bad Request" }
        return { value = {codigo: "DADOS_INVALIDOS", mensagem: "Confira os dados do Registro Clínico."} }
      }
    }
    conditional {
      if (($bruto|is_object) == false || ($bruto|keys|count) < 3 || ($bruto|keys|count) > 4 || ($bruto|get:"paciente_id"|is_int) == false || ($bruto|get:"conteudo"|is_text) == false || (($bruto|get:"liberado_paciente") != null && ($bruto|get:"liberado_paciente"|is_bool) == false) || (($bruto|get:"consulta_id") != null && ($bruto|get:"consulta_id"|is_int) == false)) {
        util.set_header { value = "HTTP/1.1 400 Bad Request" }
        return { value = {codigo: "DADOS_INVALIDOS", mensagem: "Confira os dados do Registro Clínico."} }
      }
    }
    var $conteudo { value = $bruto.conteudo|trim }
    var $liberado { value = ($bruto|get:"liberado_paciente"|default:false) }
    conditional {
      if ($bruto.paciente_id <= 0 || ($conteudo|strlen) == 0 || ($conteudo|strlen) > 8000 || (($bruto|get:"consulta_id") != null && $bruto.consulta_id <= 0)) {
        util.set_header { value = "HTTP/1.1 400 Bad Request" }
        return { value = {codigo: "DADOS_INVALIDOS", mensagem: "Confira os dados do Registro Clínico."} }
      }
    }
    db.get profissional {
      field_name = "conta_acesso_id"
      field_value = $auth.id
      output = ["id", "situacao"]
    } as $profissional
    db.get paciente {
      field_name = "id"
      field_value = $bruto.paciente_id
      output = ["id", "situacao"]
    } as $paciente
    conditional {
      if ($profissional == null || $profissional.situacao != "Ativo") {
        util.set_header { value = "HTTP/1.1 403 Forbidden" }
        return { value = {codigo: "ACESSO_NEGADO", mensagem: "Profissional sem permissão clínica ativa."} }
      }
      elseif ($paciente == null || $paciente.situacao != "ativo") {
        util.set_header { value = "HTTP/1.1 404 Not Found" }
        return { value = {codigo: "RECURSO_NAO_ENCONTRADO", mensagem: "Paciente não encontrado no escopo permitido."} }
      }
    }
    db.query prontuario_paciente {
      where = $db.prontuario_paciente.paciente_id == $paciente.id && $db.prontuario_paciente.situacao == "ativo"
      return = {type: "single"}
      output = ["id", "paciente_id"]
    } as $prontuario
    conditional {
      if ($prontuario == null) {
        util.set_header { value = "HTTP/1.1 404 Not Found" }
        return { value = {codigo: "RECURSO_NAO_ENCONTRADO", mensagem: "Prontuário não encontrado para o Paciente."} }
      }
    }
    var $consulta { value = null }
    conditional {
      if (($bruto|get:"consulta_id") != null) {
        db.get consulta {
          field_name = "id"
          field_value = $bruto.consulta_id
          output = ["id", "paciente_id", "profissional_id"]
        } as $consulta
        conditional {
          if ($consulta == null || $consulta.paciente_id != $paciente.id || $consulta.profissional_id != $profissional.id) {
            util.set_header { value = "HTTP/1.1 404 Not Found" }
            return { value = {codigo: "RECURSO_NAO_ENCONTRADO", mensagem: "Consulta não encontrada no escopo permitido."} }
          }
        }
      }
    }
    var $registro { value = null }
    try_catch {
      try {
        db.transaction {
          stack {
            db.add registro_clinico {
              data = {prontuario_id: $prontuario.id, paciente_id: $paciente.id, profissional_id: $profissional.id, consulta_id: $consulta.id, conteudo: $conteudo, liberado_paciente: $liberado, concluido: true, registrado_em: now}
            } as $registro
          }
        }
      }
      catch {
        var.update $registro { value = null }
      }
    }
    conditional {
      if ($registro == null) {
        util.set_header { value = "HTTP/1.1 503 Service Unavailable" }
        return { value = {codigo: "SERVICO_INDISPONIVEL", mensagem: "Não foi possível confirmar o Registro Clínico."} }
      }
    }
    util.set_header { value = "HTTP/1.1 201 Created" }
  }
  response = {registro_clinico: {id: $registro.id, paciente_id: $registro.paciente_id, profissional_id: $registro.profissional_id, prontuario_id: $registro.prontuario_id, liberado_paciente: $registro.liberado_paciente}}
  history = false
}
