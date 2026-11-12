// Cria retificação append-only de uma seção clínica, preservando a versão original.
query "prontuarios/{prontuario_id}/secoes/{id}/retificacao" verb=POST {
  api_group = "Sorriso Acesso"
  auth = "conta_acesso"
  input {
    int prontuario_id
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
        return { value = {codigo: "DADOS_INVALIDOS", mensagem: "Conteúdo e justificativa são obrigatórios."} }
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
        return { value = {codigo: "DADOS_INVALIDOS", mensagem: "Conteúdo e justificativa são obrigatórios e devem respeitar os limites."} }
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
    db.get prontuario_secao {
      field_name = "id"
      field_value = $input.id
      output = ["id", "prontuario_id", "paciente_id", "profissional_id", "consulta_id", "tipo", "liberado_paciente", "concluido", "versao"]
    } as $secao_original
    db.get paciente {
      field_name = "id"
      field_value = $prontuario.paciente_id
      output = ["id", "situacao"]
    } as $paciente
    conditional {
      if ($profissional == null || $profissional.situacao != "Ativo") {
        util.set_header { value = "HTTP/1.1 403 Forbidden" }
        return { value = {codigo: "ACESSO_NEGADO", mensagem: "Profissional sem permissão clínica ativa."} }
      }
      elseif ($prontuario == null || $prontuario.situacao != "ativo" || $paciente == null || $paciente.situacao != "ativo" || $secao_original == null || $secao_original.prontuario_id != $prontuario.id || $secao_original.paciente_id != $paciente.id || $secao_original.profissional_id != $profissional.id) {
        util.set_header { value = "HTTP/1.1 404 Not Found" }
        return { value = {codigo: "RECURSO_NAO_ENCONTRADO", mensagem: "Seção clínica não encontrada no escopo permitido."} }
      }
      elseif ($secao_original.concluido != true) {
        util.set_header { value = "HTTP/1.1 409 Conflict" }
        return { value = {codigo: "CONFLITO_SECAO", mensagem: "Somente seção clínica concluída pode receber retificação."} }
      }
    }
    db.query prontuario_secao {
      where = $db.prontuario_secao.prontuario_id == $prontuario.id && $db.prontuario_secao.tipo == $secao_original.tipo && ($db.prontuario_secao.id == $secao_original.id || $db.prontuario_secao.secao_original_id == $secao_original.id)
      sort = {prontuario_secao.versao: "desc", prontuario_secao.id: "desc"}
      return = {type: "single"}
      output = ["id", "versao", "secao_original_id"]
    } as $ultima_versao
    var $versao_nova { value = 1 }
    conditional {
      if ($ultima_versao != null) {
        var.update $versao_nova { value = $ultima_versao.versao + 1 }
      }
    }
    var $retificacao { value = null }
    try_catch {
      try {
        db.transaction {
          stack {
            db.add prontuario_secao {
              data = {prontuario_id: $prontuario.id, paciente_id: $prontuario.paciente_id, profissional_id: $profissional.id, consulta_id: $secao_original.consulta_id, secao_original_id: $secao_original.id, tipo: $secao_original.tipo, conteudo: $conteudo, justificativa_retificacao: $justificativa, liberado_paciente: $secao_original.liberado_paciente, concluido: true, versao: $versao_nova, criado_em: now}
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
        return { value = {codigo: "SERVICO_INDISPONIVEL", mensagem: "Não foi possível salvar a retificação da seção clínica."} }
      }
    }
    util.set_header { value = "HTTP/1.1 201 Created" }
  }
  response = {retificacao: {id: $retificacao.id, secao_original_id: $retificacao.secao_original_id, prontuario_id: $retificacao.prontuario_id, tipo: $retificacao.tipo, liberado_paciente: $retificacao.liberado_paciente, versao: $retificacao.versao, criado_em: $retificacao.criado_em}}
  history = false
}
