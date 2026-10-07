// Lista somente disponibilidades futuras, livres e de Profissionais ativos.
query disponibilidades verb=GET {
  api_group = "Sorriso Acesso"
  auth = "conta_acesso"
  input {
    int profissional_id?
    timestamp inicio?
    timestamp fim?
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
      if ($solicitante == null || $solicitante.situacao != "ativo") {
        util.set_header { value = "HTTP/1.1 403 Forbidden" }
        return { value = {codigo: "ACESSO_NEGADO", mensagem: "Conta sem permissão para consultar horários."} }
      }
    }
    conditional {
      if (($input.inicio == null) != ($input.fim == null) || ($input.inicio != null && $input.fim <= $input.inicio) || ($input.profissional_id != null && $input.profissional_id <= 0)) {
        util.set_header { value = "HTTP/1.1 400 Bad Request" }
        return { value = {codigo: "DADOS_INVALIDOS", mensagem: "Confira o Profissional e o período informados."} }
      }
    }
    db.query disponibilidade_agenda {
      join = {
        profissional: {
          table: "profissional"
          type: "inner"
          where: $db.disponibilidade_agenda.profissional_id == $db.profissional.id
        }
      }
      where = $db.disponibilidade_agenda.situacao == "disponivel" && $db.disponibilidade_agenda.inicio > now && $db.profissional.situacao == "Ativo" && ($input.profissional_id == null || $db.disponibilidade_agenda.profissional_id == $input.profissional_id) && ($input.inicio == null || $db.disponibilidade_agenda.inicio >= $input.inicio) && ($input.fim == null || $db.disponibilidade_agenda.fim <= $input.fim)
      eval = {inicio: $db.disponibilidade_agenda.inicio|format_timestamp:"c":"UTC", fim: $db.disponibilidade_agenda.fim|format_timestamp:"c":"UTC"}
      sort = {disponibilidade_agenda.inicio: "asc", disponibilidade_agenda.id: "asc"}
      return = {type: "list"}
      output = ["id", "profissional_id", "inicio", "fim", "situacao"]
    } as $disponibilidades
  }
  response = {disponibilidades: $disponibilidades}
  history = false
  guid = "pUtbBUXNHljnuXDvpE9dnmJsOXM"
}
