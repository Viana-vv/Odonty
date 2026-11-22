// Cancela ou reabre um Procedimento da Consulta sem apagar o histÃ³rico.
query "consultas/{id}/procedimentos/{consulta_procedimento_id}/situacao" verb=PATCH {
  api_group = "Sorriso Acesso"
  auth = "conta_acesso"
  input {
    int id
    int consulta_procedimento_id
  }
  stack {
    function.run sorriso_validar_sessao { input = {conta_id: $auth.id, sessao_id: $auth.extras.sessao_id} } as $sessao
    db.get conta_acesso {
      field_name = "id"
      field_value = $auth.id
      output = ["id", "perfis", "situacao"]
    } as $solicitante
    conditional {
      if ($solicitante == null || $solicitante.situacao != "ativo" || ($solicitante.perfis|intersect:["profissional"]|count) == 0) {
        util.set_header { value = "HTTP/1.1 403 Forbidden" }
        return { value = {codigo: "ACESSO_NEGADO", mensagem: "Somente Profissionais podem alterar Procedimentos."} }
      }
    }
    db.get profissional {
      field_name = "conta_acesso_id"
      field_value = $auth.id
      output = ["id", "situacao"]
    } as $profissional
    db.get consulta {
      field_name = "id"
      field_value = $input.id
      output = ["id", "profissional_id"]
    } as $consulta
    db.get consulta_procedimento {
      field_name = "id"
      field_value = $input.consulta_procedimento_id
      output = ["id", "consulta_id", "procedimento_id", "profissional_id", "situacao", "criado_em"]
    } as $vinculo
    conditional {
      if ($profissional == null || $profissional.situacao != "Ativo" || $consulta == null || $consulta.profissional_id != $profissional.id || $vinculo == null || $vinculo.consulta_id != $consulta.id) {
        util.set_header { value = "HTTP/1.1 404 Not Found" }
        return { value = {codigo: "RECURSO_NAO_ENCONTRADO", mensagem: "Procedimento não encontrado no escopo permitido."} }
      }
    }
    try_catch {
      try { util.get_raw_input { encoding = "json" } as $bruto }
      catch {
        util.set_header { value = "HTTP/1.1 400 Bad Request" }
        return { value = {codigo: "DADOS_INVALIDOS", mensagem: "Informe a situação do Procedimento."} }
      }
    }
    conditional {
      if (($bruto|get:"situacao"|is_text) == false || ($bruto.situacao != "planejado" && $bruto.situacao != "cancelado")) {
        util.set_header { value = "HTTP/1.1 400 Bad Request" }
        return { value = {codigo: "DADOS_INVALIDOS", mensagem: "Informe situação planejado ou cancelado."} }
      }
    }
    conditional {
      if ($vinculo.situacao == "realizado") {
        util.set_header { value = "HTTP/1.1 409 Conflict" }
        return { value = {codigo: "TRANSICAO_INVALIDA", mensagem: "Procedimento realizado não pode ser alterado."} }
      }
    }
    db.edit consulta_procedimento {
      field_name = "id"
      field_value = $vinculo.id
      data = {situacao: $bruto.situacao}
    } as $atualizado
  }
  response = {procedimento: {id: $atualizado.id, consulta_id: $atualizado.consulta_id, procedimento_id: $atualizado.procedimento_id, situacao: $atualizado.situacao, profissional_id: $atualizado.profissional_id, criado_em: $atualizado.criado_em|format_timestamp:"c":"UTC"}}
  history = false
  guid = "nglRNm7oxNAFLjdjJZwKPbkE838"
}
