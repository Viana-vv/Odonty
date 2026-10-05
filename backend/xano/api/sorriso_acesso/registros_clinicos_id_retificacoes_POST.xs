// Retificação append-only; a liberação do paciente permanece no Registro original.
query "registros-clinicos/{id}/retificacoes" verb=POST {
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
      if ($solicitante == null || $solicitante.situacao != "ativo" || ($solicitante.perfis|includes:"profissional") == false) {
        util.set_header { value = "HTTP/1.1 403 Forbidden" }
        return { value = {codigo: "ACESSO_NEGADO", mensagem: "Retificação permitida somente a Profissional autorizado."} }
      }
    }
    try_catch {
      try {
        util.get_raw_input { encoding = "json" } as $bruto
      }
      catch {
        util.set_header { value = "HTTP/1.1 400 Bad Request" }
        return { value = {codigo: "DADOS_INVALIDOS", mensagem: "Confira os dados da retificação."} }
      }
    }
    conditional {
      if (($bruto|is_object) == false || ($bruto|keys|count) != 2 || ($bruto|get:"conteudo"|is_text) == false || ($bruto|get:"justificativa"|is_text) == false) {
        util.set_header { value = "HTTP/1.1 400 Bad Request" }
        return { value = {codigo: "DADOS_INVALIDOS", mensagem: "Conteúdo e justificativa são obrigatórios."} }
      }
    }
    var $conteudo { value = $bruto.conteudo|trim }
    var $justificativa { value = $bruto.justificativa|trim }
    conditional {
      if (($conteudo|strlen) == 0 || ($conteudo|strlen) > 8000 || ($justificativa|strlen) == 0 || ($justificativa|strlen) > 1000) {
        util.set_header { value = "HTTP/1.1 400 Bad Request" }
        return { value = {codigo: "DADOS_INVALIDOS", mensagem: "Conteúdo e justificativa são obrigatórios."} }
      }
    }
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
    db.get registro_clinico {
      field_name = "id"
      field_value = $input.id
      output = ["id", "paciente_id", "profissional_id", "concluido"]
    } as $registro
    conditional {
      if ($registro == null || $registro.profissional_id != $profissional.id) {
        util.set_header { value = "HTTP/1.1 404 Not Found" }
        return { value = {codigo: "RECURSO_NAO_ENCONTRADO", mensagem: "Registro Clínico não encontrado no escopo permitido."} }
      }
      elseif ($registro.concluido != true) {
        util.set_header { value = "HTTP/1.1 409 Conflict" }
        return { value = {codigo: "CONFLITO_REGISTRO", mensagem: "Somente Registro Clínico concluído pode receber retificação."} }
      }
    }
    var $retificacao { value = null }
    try_catch {
      try {
        db.transaction {
          stack {
            db.add registro_clinico_retificacao {
              data = {registro_clinico_id: $registro.id, profissional_id: $profissional.id, conteudo: $conteudo, justificativa: $justificativa, criada_em: now}
            } as $retificacao
          }
        }
      }
      catch {
        var.update $retificacao { value = null }
      }
    }
    conditional {
      if ($retificacao == null) {
        util.set_header { value = "HTTP/1.1 503 Service Unavailable" }
        return { value = {codigo: "SERVICO_INDISPONIVEL", mensagem: "Não foi possível confirmar a retificação."} }
      }
    }
    util.set_header { value = "HTTP/1.1 201 Created" }
  }
  response = {retificacao: {id: $retificacao.id, registro_clinico_id: $retificacao.registro_clinico_id, profissional_id: $retificacao.profissional_id}}
  history = false
}
