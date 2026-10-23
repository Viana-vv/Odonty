// Altera somente a situação do cadastro; não remove Consultas ou Agenda.
query "profissionais/{id}/situacao" verb=PATCH {
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
      if ($solicitante == null || $solicitante.situacao != "ativo" || ($solicitante.perfis|intersect:["administrador"]|count) == 0) {
        util.set_header { value = "HTTP/1.1 403 Forbidden" }
        return { value = {codigo: "ACESSO_NEGADO", mensagem: "Alteração permitida somente ao Administrador."} }
      }
    }
    conditional {
      if ($input.id <= 0) {
        util.set_header { value = "HTTP/1.1 400 Bad Request" }
        return { value = {codigo: "DADOS_INVALIDOS", mensagem: "Identificador de Profissional inválido."} }
      }
    }
    try_catch {
      try {
        util.get_raw_input { encoding = "json" } as $bruto
      }
      catch {
        util.set_header { value = "HTTP/1.1 400 Bad Request" }
        return { value = {codigo: "DADOS_INVALIDOS", mensagem: "Informe a situação do Profissional."} }
      }
    }
    conditional {
      if (($bruto|is_object) == false || ($bruto|keys|count) != 1 || ($bruto|get:"situacao"|is_text) == false || ($bruto.situacao != "ativo" && $bruto.situacao != "inativo")) {
        util.set_header { value = "HTTP/1.1 400 Bad Request" }
        return { value = {codigo: "DADOS_INVALIDOS", mensagem: "Informe a situação ativo ou inativo."} }
      }
    }
    var $situacao_armazenada { value = "Ativo" }
    conditional {
      if ($bruto.situacao == "inativo") {
        var.update $situacao_armazenada { value = "Inativo" }
      }
    }
    db.get profissional {
      field_name = "id"
      field_value = $input.id
      output = ["id", "agenda_lock_version"]
    } as $existente
    conditional {
      if ($existente == null) {
        util.set_header { value = "HTTP/1.1 404 Not Found" }
        return { value = {codigo: "RECURSO_NAO_ENCONTRADO", mensagem: "Profissional não encontrado."} }
      }
    }
    db.transaction {
      stack {
        db.edit profissional {
          field_name = "id"
          field_value = $input.id
          data = {situacao: $situacao_armazenada, agenda_lock_version: (($existente.agenda_lock_version|default:0) + 1), atualizado_em: now}
        } as $atualizado
      }
    }
  }
  response = {profissional: {id: $atualizado.id, situacao: ($atualizado.situacao|to_lower)}}
  history = false
}
