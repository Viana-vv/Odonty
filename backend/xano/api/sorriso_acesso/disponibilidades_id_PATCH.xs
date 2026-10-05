// Atualiza somente intervalo ou bloqueio de disponibilidade livre e futura.
query "disponibilidades/{id}" verb=PATCH {
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
        return { value = {codigo: "DADOS_INVALIDOS", mensagem: "Informe campos válidos para atualização."} }
      }
    }
    var $campo_invalido { value = false }
    foreach ($bruto|keys) {
      each as $chave {
        conditional {
          if ($chave not in ["inicio", "fim", "situacao"]) {
            var.update $campo_invalido { value = true }
          }
        }
      }
    }
    conditional {
      if (($bruto|is_object) == false || $campo_invalido || ($bruto|keys|count) < 1 || ($bruto|keys|count) > 3 || (($bruto|get:"inicio") != null && ($bruto|get:"fim") == null) || (($bruto|get:"inicio") == null && ($bruto|get:"fim") != null) || (($bruto|get:"situacao") != null && ($bruto|get:"situacao") != "disponivel" && ($bruto|get:"situacao") != "bloqueado") || (($bruto|get:"inicio") == null && ($bruto|get:"situacao") == null)) {
        util.set_header { value = "HTTP/1.1 400 Bad Request" }
        return { value = {codigo: "DADOS_INVALIDOS", mensagem: "Informe intervalo completo ou situação permitida."} }
      }
    }
    db.get disponibilidade_agenda {
      field_name = "id"
      field_value = $input.id
      output = ["id", "profissional_id", "inicio", "fim", "situacao"]
    } as $disponibilidade
    conditional {
      if ($disponibilidade == null) {
        util.set_header { value = "HTTP/1.1 404 Not Found" }
        return { value = {codigo: "RECURSO_NAO_ENCONTRADO", mensagem: "Disponibilidade não encontrada."} }
      }
    }
    db.get profissional {
      field_name = "id"
      field_value = $disponibilidade.profissional_id
      output = ["id", "conta_acesso_id", "situacao", "agenda_lock_version"]
    } as $profissional
    conditional {
      if (($solicitante.perfis|includes:"profissional") && $profissional.conta_acesso_id != $auth.id) {
        util.set_header { value = "HTTP/1.1 404 Not Found" }
        return { value = {codigo: "RECURSO_NAO_ENCONTRADO", mensagem: "Disponibilidade não encontrada."} }
      }
      elseif ($disponibilidade.situacao == "reservado" || $disponibilidade.situacao == "indisponivel" || $disponibilidade.inicio <= now) {
        util.set_header { value = "HTTP/1.1 409 Conflict" }
        return { value = {codigo: "CONFLITO_AGENDA", mensagem: "Disponibilidade reservada ou passada não pode ser alterada."} }
      }
    }
    var $inicio { value = $disponibilidade.inicio }
    var $fim { value = $disponibilidade.fim }
    var $situacao { value = $disponibilidade.situacao }
    conditional {
      if (($bruto|get:"inicio") != null) {
        conditional {
          if (($bruto.inicio|is_text) == false || ($bruto.fim|is_text) == false || $bruto.inicio >= $bruto.fim || $bruto.inicio <= now) {
            util.set_header { value = "HTTP/1.1 400 Bad Request" }
            return { value = {codigo: "DADOS_INVALIDOS", mensagem: "Informe um intervalo futuro válido."} }
          }
        }
        var.update $inicio { value = $bruto.inicio }
        var.update $fim { value = $bruto.fim }
      }
    }
    conditional {
      if (($bruto|get:"situacao") != null) {
        var.update $situacao { value = $bruto.situacao }
      }
    }
    var $conflito { value = false }
    var $atualizada { value = null }
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
              where = $db.disponibilidade_agenda.id != $disponibilidade.id && $db.disponibilidade_agenda.profissional_id == $profissional.id && $db.disponibilidade_agenda.inicio < $fim && $db.disponibilidade_agenda.fim > $inicio
              return = {type: "list"}
              output = ["id"]
            } as $sobreposicoes
            conditional {
              if (($sobreposicoes|count) > 0) {
                var.update $conflito { value = true }
              }
              else {
                db.edit disponibilidade_agenda {
                  field_name = "id"
                  field_value = $disponibilidade.id
                  data = {inicio: $inicio, fim: $fim, situacao: $situacao, atualizado_em: now}
                } as $atualizada
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
        return { value = {codigo: "CONFLITO_AGENDA", mensagem: "O intervalo se sobrepõe a outro horário ou não pôde ser reservado."} }
      }
    }
    conditional {
      if ($atualizada == null) {
        util.set_header { value = "HTTP/1.1 503 Service Unavailable" }
        return { value = {codigo: "SERVICO_INDISPONIVEL", mensagem: "Não foi possível confirmar a atualização."} }
      }
    }
  }
  response = {disponibilidade: {id: $atualizada.id, profissional_id: $atualizada.profissional_id, inicio: $atualizada.inicio, fim: $atualizada.fim, situacao: $atualizada.situacao}}
  history = false
}
