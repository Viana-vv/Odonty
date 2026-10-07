// Escopo aplicado no Xano; listas administrativas nunca incluem conteúdo clínico.
query consultas verb=GET {
  api_group = "Sorriso Acesso"
  auth = "conta_acesso"
  input {
    int paciente_id?
    int profissional_id?
    text situacao?
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
      if ($solicitante == null || $solicitante.situacao != "ativo" || ($solicitante.perfis|intersect:["paciente", "profissional", "administrador", "recepcionista"]|count) == 0) {
        util.set_header { value = "HTTP/1.1 403 Forbidden" }
        return { value = {codigo: "ACESSO_NEGADO", mensagem: "Conta sem permissão para consultar Consultas."} }
      }
      elseif (($input.paciente_id != null && $input.paciente_id <= 0) || ($input.profissional_id != null && $input.profissional_id <= 0) || (($input.inicio == null) != ($input.fim == null)) || ($input.inicio != null && $input.fim <= $input.inicio) || ($input.situacao != null && $input.situacao not in ["Agendada", "Confirmada", "Em atendimento", "Realizada", "Cancelada", "Falta"])) {
        util.set_header { value = "HTTP/1.1 400 Bad Request" }
        return { value = {codigo: "DADOS_INVALIDOS", mensagem: "Confira os filtros da Consulta."} }
      }
    }
    var $paciente_escopo { value = $input.paciente_id }
    var $profissional_escopo { value = null }
    var $situacao_armazenada { value = $input.situacao }
    conditional {
      if ($input.situacao == "Realizada") {
        var.update $situacao_armazenada { value = "Concluída" }
      }
    }
    conditional {
      if (($solicitante.perfis|includes:"paciente")) {
        db.get paciente {
          field_name = "conta_acesso_id"
          field_value = $auth.id
          output = ["id", "situacao"]
        } as $paciente_autenticado
        conditional {
          if ($paciente_autenticado == null || $paciente_autenticado.situacao != "ativo") {
            util.set_header { value = "HTTP/1.1 404 Not Found" }
            return { value = {codigo: "RECURSO_NAO_ENCONTRADO", mensagem: "Consultas não encontradas no escopo permitido."} }
          }
        }
        var.update $paciente_escopo { value = $paciente_autenticado.id }
      }
      elseif (($solicitante.perfis|includes:"profissional")) {
        db.get profissional {
          field_name = "conta_acesso_id"
          field_value = $auth.id
          output = ["id", "situacao"]
        } as $profissional_autenticado
        conditional {
          if ($profissional_autenticado == null || $profissional_autenticado.situacao != "Ativo") {
            util.set_header { value = "HTTP/1.1 403 Forbidden" }
            return { value = {codigo: "ACESSO_NEGADO", mensagem: "Profissional sem acesso à Agenda."} }
          }
        }
        var.update $profissional_escopo { value = $profissional_autenticado.id }
      }
    }
    db.query consulta {
      join = {
        consulta_disponibilidade: {
          table: "consulta_disponibilidade"
          type: "left"
          where: $db.consulta.id == $db.consulta_disponibilidade.consulta_id
        },
        paciente: {
          table: "paciente"
          type: "inner"
          where: $db.consulta.paciente_id == $db.paciente.id
        },
        profissional: {
          table: "profissional"
          type: "inner"
          where: $db.consulta.profissional_id == $db.profissional.id
        },
        procedimento: {
          table: "procedimento"
          type: "left"
          where: $db.consulta.procedimento_id == $db.procedimento.id
        },
        consulta_procedimento: {
          table: "consulta_procedimento"
          type: "left"
          where: $db.consulta.id == $db.consulta_procedimento.consulta_id
        },
        procedimento_vinculado: {
          table: "procedimento"
          type: "left"
          where: $db.consulta_procedimento.procedimento_id == $db.procedimento_vinculado.id
        }
      }
      where = ($paciente_escopo == null || $db.consulta.paciente_id == $paciente_escopo) && ($profissional_escopo == null || $db.consulta.profissional_id == $profissional_escopo) && ($input.profissional_id == null || $db.consulta.profissional_id == $input.profissional_id) && ($input.situacao == null || $db.consulta.situacao == $situacao_armazenada) && ($input.inicio == null || ($db.consulta.inicio_em >= $input.inicio && $db.consulta.fim_em <= $input.fim))
      eval = {inicio_em: $db.consulta.inicio_em|format_timestamp:"c":"UTC", fim_em: $db.consulta.fim_em|format_timestamp:"c":"UTC", disponibilidade_id: $db.consulta_disponibilidade.disponibilidade_id, situacao: $db.consulta.situacao|replace:"Concluída":"Realizada", paciente_nome: $db.paciente.nome, profissional_nome: $db.profissional.nome, procedimento_nome: $db.procedimento.nome, procedimento_vinculado_nome: $db.procedimento_vinculado.nome}
      sort = {consulta.inicio_em: "desc", consulta.id: "desc"}
      return = {type: "list"}
      output = ["id", "paciente_id", "profissional_id", "inicio_em", "fim_em", "situacao", "disponibilidade_id", "paciente_nome", "profissional_nome", "procedimento_nome", "procedimento_vinculado_nome"]
    } as $consultas
  }
  response = {consultas: $consultas}
  history = false
  guid = "p107TSKMEOjzrvK2A7U3vHSa5Q8"
}
