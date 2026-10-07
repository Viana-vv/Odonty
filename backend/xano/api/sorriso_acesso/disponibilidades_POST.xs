// Cria intervalo futuro sem sobreposição, com autorização no backend.
query disponibilidades verb=POST {
  api_group = "Sorriso Acesso"
  auth = "conta_acesso"
  input { }
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
      if ($solicitante == null || $solicitante.situacao != "ativo" || ($solicitante.perfis|intersect:["profissional", "administrador", "recepcionista"]|count) == 0) {
        util.set_header { value = "HTTP/1.1 403 Forbidden" }
        return { value = {codigo: "ACESSO_NEGADO", mensagem: "Conta sem permissão para administrar a Agenda."} }
      }
    }
    try_catch {
      try {
        util.get_raw_input { encoding = "json" } as $bruto
      }
      catch {
        util.set_header { value = "HTTP/1.1 400 Bad Request" }
        return { value = {codigo: "DADOS_INVALIDOS", mensagem: "Confira os dados da Disponibilidade."} }
      }
    }
    var $campo_invalido { value = false }
    foreach ($bruto|keys) {
      each as $chave {
        conditional {
          if ($chave not in ["profissional_id", "inicio", "fim"]) {
            var.update $campo_invalido { value = true }
          }
        }
      }
    }
    conditional {
      if (($bruto|is_object) == false || $campo_invalido || ($bruto|keys|count) != 3 || ($bruto|get:"profissional_id"|is_int) == false || ($bruto|get:"inicio"|is_text) == false || ($bruto|get:"fim"|is_text) == false) {
        util.set_header { value = "HTTP/1.1 400 Bad Request" }
        return { value = {codigo: "DADOS_INVALIDOS", mensagem: "Confira os dados da Disponibilidade."} }
      }
    }
    conditional {
      if ($bruto.profissional_id <= 0 || $bruto.inicio >= $bruto.fim || $bruto.inicio <= now) {
        util.set_header { value = "HTTP/1.1 400 Bad Request" }
        return { value = {codigo: "DADOS_INVALIDOS", mensagem: "Informe um intervalo futuro válido."} }
      }
    }
    db.get profissional {
      field_name = "id"
      field_value = $bruto.profissional_id
      output = ["id", "conta_acesso_id", "situacao", "agenda_lock_version"]
    } as $profissional
    conditional {
      if ($profissional == null || $profissional.situacao != "Ativo") {
        util.set_header { value = "HTTP/1.1 400 Bad Request" }
        return { value = {codigo: "DADOS_INVALIDOS", mensagem: "Profissional indisponível para novos horários."} }
      }
      elseif (($solicitante.perfis|includes:"profissional") && $profissional.conta_acesso_id != $auth.id) {
        util.set_header { value = "HTTP/1.1 403 Forbidden" }
        return { value = {codigo: "ACESSO_NEGADO", mensagem: "Profissional só pode administrar a própria Agenda."} }
      }
    }
    var $conflito { value = false }
    var $criada { value = null }
    try_catch {
      try {
        db.transaction {
          stack {
            db.edit profissional {
              field_name = "id"
              field_value = $profissional.id
              data = {agenda_lock_version: (($profissional.agenda_lock_version|default:0) + 1)}
            } as $trava_agenda
            db.query disponibilidade_agenda {
              where = $db.disponibilidade_agenda.profissional_id == $profissional.id && $db.disponibilidade_agenda.inicio < $bruto.fim && $db.disponibilidade_agenda.fim > $bruto.inicio
              return = {type: "list"}
              output = ["id"]
            } as $sobreposicoes
            conditional {
              if (($sobreposicoes|count) > 0) {
                var.update $conflito { value = true }
              }
              else {
                db.add disponibilidade_agenda {
                  data = {profissional_id: $profissional.id, inicio: $bruto.inicio, fim: $bruto.fim, situacao: "disponivel", criado_em: now, atualizado_em: now}
                } as $criada
              }
            }
          }
        }
      }
      catch {
        var.update $conflito { value = true }
      }
    }
    conditional {
      if ($conflito) {
        util.set_header { value = "HTTP/1.1 409 Conflict" }
        return { value = {codigo: "CONFLITO_AGENDA", mensagem: "Já existe um horário sobreposto para este Profissional."} }
      }
    }
    conditional {
      if ($criada == null) {
        util.set_header { value = "HTTP/1.1 503 Service Unavailable" }
        return { value = {codigo: "SERVICO_INDISPONIVEL", mensagem: "Não foi possível confirmar a Disponibilidade."} }
      }
    }
    util.set_header { value = "HTTP/1.1 201 Created" }
  }
  response = {disponibilidade: {id: $criada.id, profissional_id: $criada.profissional_id, inicio: $criada.inicio|format_timestamp:"c":"UTC", fim: $criada.fim|format_timestamp:"c":"UTC", situacao: $criada.situacao}}
  history = false
  guid = "AaNU0ytM5bB2ANS_yMc5qsGG9oM"
}
