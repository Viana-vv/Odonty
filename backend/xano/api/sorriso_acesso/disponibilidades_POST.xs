// Cria intervalo futuro sem sobreposição, com autorização no backend.
query disponibilidades verb=POST {
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
          if ($chave != "profissional_id" && $chave != "inicio" && $chave != "fim") {
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
      if ($input.profissional_id <= 0 || $input.inicio >= $input.fim || $input.inicio <= now) {
        util.set_header { value = "HTTP/1.1 400 Bad Request" }
        return { value = {codigo: "DADOS_INVALIDOS", mensagem: "Informe um intervalo futuro válido."} }
      }
    }
    db.get profissional {
      field_name = "id"
      field_value = $input.profissional_id
      output = ["id", "conta_acesso_id", "situacao"]
    } as $profissional
    conditional {
      if ($profissional == null || $profissional.situacao != "Ativo") {
        util.set_header { value = "HTTP/1.1 400 Bad Request" }
        return { value = {codigo: "DADOS_INVALIDOS", mensagem: "Profissional indisponível para novos horários."} }
      }
      elseif (($solicitante.perfis|intersect:["profissional"]|count) > 0 && $profissional.conta_acesso_id != $auth.id) {
        util.set_header { value = "HTTP/1.1 403 Forbidden" }
        return { value = {codigo: "ACESSO_NEGADO", mensagem: "Profissional só pode administrar a própria Agenda."} }
      }
    }
    var $conflito { value = false }
    var $falha_servico { value = false }
    var $criada { value = null }
    try_catch {
      try {
        db.transaction {
          stack {
            db.query agenda_controle {
              where = $db.agenda_controle.escopo == "profissional" && $db.agenda_controle.escopo_id == $profissional.id
              return = {type: "single"}
              output = ["id", "versao"]
            } as $controle_profissional
            conditional {
              if ($controle_profissional == null) {
                db.add agenda_controle {
                  data = {escopo: "profissional", escopo_id: $profissional.id, versao: 1, atualizado_em: now}
                } as $novo_controle_profissional
              }
              else {
                db.edit agenda_controle {
                  field_name = "id"
                  field_value = $controle_profissional.id
                  data = {versao: ($controle_profissional.versao + 1), atualizado_em: now}
                } as $controle_profissional_atualizado
              }
            }
            db.query disponibilidade_agenda {
              where = $db.disponibilidade_agenda.profissional_id == $profissional.id && $db.disponibilidade_agenda.inicio < $input.fim && $db.disponibilidade_agenda.fim > $input.inicio
              return = {type: "list"}
              output = ["id"]
            } as $sobreposicoes
            conditional {
              if (($sobreposicoes|count) > 0) {
                var.update $conflito { value = true }
              }
              else {
                db.add disponibilidade_agenda {
                  data = {profissional_id: $profissional.id, inicio: $input.inicio, fim: $input.fim, situacao: "disponivel", criado_em: now, atualizado_em: now}
                } as $criada
              }
            }
          }
        }
      }
      catch {
        var.update $falha_servico { value = true }
      }
    }
    conditional {
      if ($conflito) {
        util.set_header { value = "HTTP/1.1 409 Conflict" }
        return { value = {codigo: "CONFLITO_AGENDA", mensagem: "Já existe um horário sobreposto para este Profissional."} }
      }
    }
    conditional {
      if ($falha_servico || $criada == null) {
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
