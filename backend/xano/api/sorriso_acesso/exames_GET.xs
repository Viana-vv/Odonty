// Lista Exames no escopo clínico da Conta de Acesso autenticada.
query "exames" verb=GET {
  api_group = "Sorriso Acesso"
  auth = "conta_acesso"
  input { int paciente_id? int consulta_id? }
  stack {
    util.set_header { value = "Cache-Control: no-store" duplicates = "replace" }
    function.run sorriso_validar_sessao { input = {conta_id: $auth.id, sessao_id: $auth.extras.sessao_id} } as $sessao
    db.get conta_acesso { field_name = "id" field_value = $auth.id output = ["id", "perfis", "situacao"] } as $conta
    conditional {
      if ($conta == null || $conta.situacao != "ativo" || (($conta.perfis|intersect:["profissional", "paciente"]|count) == 0)) {
        util.set_header { value = "HTTP/1.1 403 Forbidden" }
        return { value = {codigo: "ACESSO_NEGADO", mensagem: "Conta sem permissão para consultar Exames."} }
      }
    }
    var $filtro_paciente { value = $input.paciente_id }
    var $filtro_profissional { value = null }
    conditional {
      if (($conta.perfis|includes:"paciente")) {
        db.get paciente { field_name = "conta_acesso_id" field_value = $auth.id output = ["id", "situacao"] } as $paciente
        conditional { if ($paciente == null || $paciente.situacao != "ativo") { util.set_header { value = "HTTP/1.1 404 Not Found" } return { value = {codigo: "RECURSO_NAO_ENCONTRADO", mensagem: "Exames não encontrados."} } } }
        var.update $filtro_paciente { value = $paciente.id }
      }
      else {
        db.get profissional { field_name = "conta_acesso_id" field_value = $auth.id output = ["id", "situacao"] } as $profissional
        conditional { if ($profissional == null || $profissional.situacao != "Ativo") { util.set_header { value = "HTTP/1.1 403 Forbidden" } return { value = {codigo: "ACESSO_NEGADO", mensagem: "Profissional sem permissão clínica ativa."} } } }
        var.update $filtro_profissional { value = $profissional.id }
      }
    }
    var $exames { value = [] }
    conditional {
      if ($filtro_profissional != null) {
        db.query exame { where = $db.exame.profissional_id == $filtro_profissional sort = {exame.solicitado_em: "desc"} return = {type: "list"} output = ["id", "paciente_id", "consulta_id", "profissional_id", "tipo", "situacao", "solicitado_em", "realizado_em", "resultado", "observacoes"] } as $lista
      }
      else {
        db.query exame { where = $db.exame.paciente_id == $filtro_paciente && $db.exame.situacao == "Resultado disponível" sort = {exame.solicitado_em: "desc"} return = {type: "list"} output = ["id", "paciente_id", "consulta_id", "profissional_id", "tipo", "situacao", "solicitado_em", "realizado_em", "resultado", "observacoes"] } as $lista
      }
    }
    var.update $exames { value = $lista }
  }
  response = {exames: $exames}
  history = false
}
