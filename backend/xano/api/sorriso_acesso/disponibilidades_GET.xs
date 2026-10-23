// Lista disponibilidades futuras livres ou bloqueadas de Profissionais ativos.
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
    var $eh_paciente { value = false }
    var $eh_profissional { value = false }
    conditional {
      if (($solicitante.perfis|intersect:["paciente"]|count) > 0) {
        var.update $eh_paciente { value = true }
      }
    }
    conditional {
      if (($solicitante.perfis|intersect:["profissional"]|count) > 0) {
        var.update $eh_profissional { value = true }
      }
    }
    conditional {
      if (($input.inicio == null) != ($input.fim == null) || ($input.inicio != null && $input.fim <= $input.inicio) || ($input.profissional_id != null && $input.profissional_id <= 0)) {
        util.set_header { value = "HTTP/1.1 400 Bad Request" }
        return { value = {codigo: "DADOS_INVALIDOS", mensagem: "Confira o Profissional e o período informados."} }
      }
    }
    db.query disponibilidade_agenda {
      sort = {disponibilidade_agenda.inicio: "asc", disponibilidade_agenda.id: "asc"}
      return = {type: "list"}
      output = ["id", "profissional_id", "inicio", "fim", "situacao"]
    } as $disponibilidades
    var $disponibilidades_formatadas { value = [] }
    foreach ($disponibilidades) {
      each as $disponibilidade {
        db.get profissional {
          field_name = "id"
          field_value = $disponibilidade.profissional_id
          output = ["id", "nome", "situacao", "conta_acesso_id"]
        } as $profissional
        var $incluir_disponibilidade { value = true }
        conditional {
          if ($profissional == null || $profissional.situacao != "Ativo" || $disponibilidade.inicio <= now || ($eh_paciente == true && $disponibilidade.situacao != "disponivel") || ($eh_profissional == true && $profissional.conta_acesso_id != $auth.id) || ($input.profissional_id != null && $disponibilidade.profissional_id != $input.profissional_id) || ($input.inicio != null && $disponibilidade.inicio < $input.inicio) || ($input.fim != null && $disponibilidade.fim > $input.fim)) {
            var.update $incluir_disponibilidade { value = false }
          }
        }
        conditional {
          if ($incluir_disponibilidade) {
        var $inicio_iso { value = $disponibilidade.inicio|format_timestamp:"c":"UTC" }
        var $fim_iso { value = $disponibilidade.fim|format_timestamp:"c":"UTC" }
        var $disponibilidade_formatada {
          value = {id: $disponibilidade.id, profissional_id: $disponibilidade.profissional_id, profissional_nome: $profissional.nome, inicio: $inicio_iso, fim: $fim_iso, situacao: $disponibilidade.situacao}
        }
        var.update $disponibilidades_formatadas {
          value = $disponibilidades_formatadas|push:$disponibilidade_formatada
        }
          }
        }
      }
    }
  }
  response = {disponibilidades: $disponibilidades_formatadas}
  history = false
  guid = "pUtbBUXNHljnuXDvpE9dnmJsOXM"
}
