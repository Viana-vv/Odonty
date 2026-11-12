// Cria uma seção clínica versionada somente por Profissional ativo e autorizado.
query "prontuarios/{prontuario_id}/secoes" verb=POST {
  api_group = "Sorriso Acesso"
  auth = "conta_acesso"
  input {
    int prontuario_id
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
      if ($solicitante == null || $solicitante.situacao != "ativo" || ($solicitante.perfis|includes:"profissional") == false) {
        util.set_header { value = "HTTP/1.1 403 Forbidden" }
        return { value = {codigo: "ACESSO_NEGADO", mensagem: "Seções clínicas permitidas somente a Profissional autorizado."} }
      }
    }
    try_catch {
      try {
        util.get_raw_input { encoding = "json" } as $bruto
      }
      catch {
        util.set_header { value = "HTTP/1.1 400 Bad Request" }
        return { value = {codigo: "DADOS_INVALIDOS", mensagem: "Confira os dados da seção clínica."} }
      }
    }
    conditional {
      if (($bruto|is_object) == false || ($bruto|keys|count) < 2 || ($bruto|keys|count) > 5 || ($bruto|get:"paciente_id"|is_int) == false || ($bruto|get:"tipo"|is_text) == false || ($bruto|get:"conteudo"|is_text) == false || (($bruto|get:"consulta_id") != null && ($bruto|get:"consulta_id"|is_int) == false) || (($bruto|get:"liberado_paciente") != null && ($bruto|get:"liberado_paciente"|is_bool) == false)) {
        util.set_header { value = "HTTP/1.1 400 Bad Request" }
        return { value = {codigo: "DADOS_INVALIDOS", mensagem: "Paciente, tipo e conteúdo da seção são obrigatórios."} }
      }
    }
    var $tipo { value = $bruto.tipo|trim }
    var $conteudo { value = $bruto.conteudo|trim }
    var $liberado { value = ($bruto|get:"liberado_paciente"|default:false) }
    conditional {
      if ($bruto.paciente_id <= 0 || ($tipo|strlen) == 0 || ($conteudo|strlen) == 0 || ($conteudo|strlen) > 8000 || (($bruto|get:"consulta_id") != null && $bruto.consulta_id <= 0) || ($tipo != "Anamnese" && $tipo != "Histórico Odontológico" && $tipo != "Exame Clínico" && $tipo != "Diagnóstico" && $tipo != "Plano de Tratamento" && $tipo != "Odontograma" && $tipo != "Prescrição" && $tipo != "Documento")) {
        util.set_header { value = "HTTP/1.1 400 Bad Request" }
        return { value = {codigo: "DADOS_INVALIDOS", mensagem: "Informe um tipo permitido e conteúdo não vazio para a seção."} }
      }
    }
    db.get profissional {
      field_name = "conta_acesso_id"
      field_value = $auth.id
      output = ["id", "situacao"]
    } as $profissional
    db.get prontuario_paciente {
      field_name = "id"
      field_value = $input.prontuario_id
      output = ["id", "paciente_id", "situacao"]
    } as $prontuario
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
      elseif ($prontuario == null || $prontuario.situacao != "ativo" || $paciente == null || $paciente.situacao != "ativo" || $prontuario.paciente_id != $paciente.id) {
        util.set_header { value = "HTTP/1.1 404 Not Found" }
        return { value = {codigo: "RECURSO_NAO_ENCONTRADO", mensagem: "Prontuário não encontrado no escopo permitido."} }
      }
    }
    var $consulta { value = null }
    var $consulta_escopo { value = null }
    var $consulta_id_resolvida { value = null }
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
        var.update $consulta_id_resolvida { value = $consulta.id }
      }
      else {
        db.query consulta {
          where = $db.consulta.paciente_id == $paciente.id && $db.consulta.profissional_id == $profissional.id
          return = {type: "single"}
          output = ["id"]
        } as $consulta_escopo
        conditional {
          if ($consulta_escopo == null) {
            util.set_header { value = "HTTP/1.1 404 Not Found" }
            return { value = {codigo: "RECURSO_NAO_ENCONTRADO", mensagem: "Paciente não encontrado no escopo permitido."} }
          }
        }
        var.update $consulta_id_resolvida { value = $consulta_escopo.id }
      }
    }
    var $secao { value = null }
    try_catch {
      try {
        db.transaction {
          stack {
            db.add prontuario_secao {
              data = {prontuario_id: $prontuario.id, paciente_id: $paciente.id, profissional_id: $profissional.id, consulta_id: $consulta_id_resolvida, tipo: $tipo, conteudo: $conteudo, liberado_paciente: $liberado, concluido: true, versao: 1, criado_em: now}
            } as $secao
          }
        }
      }
      catch {
        var.update $secao { value = null }
      }
    }
    conditional {
      if ($secao == null) {
        util.set_header { value = "HTTP/1.1 503 Service Unavailable" }
        return { value = {codigo: "SERVICO_INDISPONIVEL", mensagem: "Não foi possível salvar a seção clínica."} }
      }
    }
    util.set_header { value = "HTTP/1.1 201 Created" }
  }
  response = {secao: {id: $secao.id, prontuario_id: $secao.prontuario_id, paciente_id: $secao.paciente_id, profissional_id: $secao.profissional_id, consulta_id: $secao.consulta_id, tipo: $secao.tipo, liberado_paciente: $secao.liberado_paciente, versao: $secao.versao, criado_em: $secao.criado_em}}
  history = false
}
