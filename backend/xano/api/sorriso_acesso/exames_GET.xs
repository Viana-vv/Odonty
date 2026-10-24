query "exames" verb=GET {
  api_group = "Sorriso Acesso"
  auth = "conta_acesso"
  input {
    int paciente_id?
    int consulta_id?
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
    } as $conta
    conditional {
      if ($conta == null || $conta.situacao != "ativo") {
        util.set_header {
          value = "HTTP/1.1 403 Forbidden"
        }
        return {
          value = {codigo: "ACESSO_NEGADO", mensagem: "Conta sem permissão para consultar Exames."}
        }
      }
    }
    db.get profissional {
      field_name = "conta_acesso_id"
      field_value = $auth.id
      output = ["id", "situacao"]
    } as $profissional
    conditional {
      if (($conta.perfis|intersect:["profissional"]|count) == 0 || $profissional == null || $profissional.situacao != "Ativo") {
        util.set_header {
          value = "HTTP/1.1 403 Forbidden"
        }
        return {
          value = {codigo: "ACESSO_NEGADO", mensagem: "Exames disponíveis somente para Profissional autorizado."}
        }
      }
    }
    db.query exame {
      where = $db.exame.profissional_id == $profissional.id
      sort = {exame.solicitado_em: "desc"}
      return = {type: "list"}
      output = ["id", "paciente_id", "consulta_id", "profissional_id", "tipo", "situacao", "solicitado_em", "realizado_em", "resultado", "observacoes"]
    } as $exames
  }
  response = {exames: $exames}
  history = false
}
