// Adiciona um Procedimento ativo à Consulta do Profissional autenticado.
query "consultas/{id}/procedimentos" verb=POST {
  api_group = "Sorriso Acesso"
  auth = "conta_acesso"
  input { int id }
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
        return { value = {codigo: "ACESSO_NEGADO", mensagem: "Somente Profissionais podem adicionar Procedimentos."} }
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
    conditional {
      if ($profissional == null || $profissional.situacao != "Ativo" || $consulta == null || $consulta.profissional_id != $profissional.id) {
        util.set_header { value = "HTTP/1.1 404 Not Found" }
        return { value = {codigo: "RECURSO_NAO_ENCONTRADO", mensagem: "Consulta não encontrada no escopo permitido."} }
      }
    }
    try_catch {
      try { util.get_raw_input { encoding = "json" } as $bruto }
      catch {
        util.set_header { value = "HTTP/1.1 400 Bad Request" }
        return { value = {codigo: "DADOS_INVALIDOS", mensagem: "Informe o Procedimento."} }
      }
    }
    conditional {
      if (($bruto|get:"procedimento_id"|is_int) == false || $bruto.procedimento_id <= 0) {
        util.set_header { value = "HTTP/1.1 400 Bad Request" }
        return { value = {codigo: "DADOS_INVALIDOS", mensagem: "Informe um Procedimento válido."} }
      }
    }
    db.get procedimento {
      field_name = "id"
      field_value = $bruto.procedimento_id
      output = ["id", "nome", "ativo"]
    } as $procedimento
    conditional {
      if ($procedimento == null || $procedimento.ativo != true) {
        util.set_header { value = "HTTP/1.1 409 Conflict" }
        return { value = {codigo: "PROCEDIMENTO_INATIVO", mensagem: "Somente Procedimentos ativos podem ser adicionados."} }
      }
    }
    db.query consulta_procedimento {
      where = $db.consulta_procedimento.consulta_id == $consulta.id && $db.consulta_procedimento.procedimento_id == $procedimento.id
      return = {type: "single"}
      output = ["id", "situacao"]
    } as $existente
    conditional {
      if ($existente != null && $existente.situacao != "cancelado") {
        util.set_header { value = "HTTP/1.1 409 Conflict" }
        return { value = {codigo: "DUPLICIDADE", mensagem: "Este Procedimento já está vinculado à Consulta."} }
      }
    }
    conditional {
      if ($existente != null) {
        db.edit consulta_procedimento {
          field_name = "id"
          field_value = $existente.id
          data = {situacao: "planejado", profissional_id: $profissional.id, realizado_por_profissional_id: null, realizado_em: null}
        } as $vinculo
      }
      else {
        db.add consulta_procedimento {
          data = {consulta_id: $consulta.id, procedimento_id: $procedimento.id, profissional_id: $profissional.id, situacao: "planejado", criado_em: now}
        } as $vinculo_novo
        var $vinculo { value = $vinculo_novo }
      }
    }
  }
  response = {procedimento: {id: $vinculo.id, consulta_id: $vinculo.consulta_id, procedimento_id: $vinculo.procedimento_id, procedimento_nome: $procedimento.nome, situacao: $vinculo.situacao, profissional_id: $vinculo.profissional_id}}
  history = false
  guid = "rm2yhNie2tzbm8ahy93zrSWFqwE"
}
