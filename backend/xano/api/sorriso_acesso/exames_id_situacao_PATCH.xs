// Atualiza situação/resultado sem apagar o histórico do Exame.
query "exames/{exame_id}/situacao" verb=PATCH {
  api_group = "Sorriso Acesso"
  auth = "conta_acesso"
  input { int exame_id }
  stack {
    function.run sorriso_validar_sessao { input = {conta_id: $auth.id, sessao_id: $auth.extras.sessao_id} } as $sessao
    util.get_raw_input { encoding = "json" } as $bruto
    db.get profissional { field_name = "conta_acesso_id" field_value = $auth.id output = ["id", "situacao"] } as $profissional
    db.get exame { field_name = "id" field_value = $input.exame_id output = ["id", "paciente_id", "consulta_id", "profissional_id", "tipo", "situacao", "solicitado_em", "realizado_em", "resultado", "observacoes"] } as $exame
    conditional { if ($profissional == null || $profissional.situacao != "Ativo" || $exame == null || $exame.profissional_id != $profissional.id) { util.set_header { value = "HTTP/1.1 403 Forbidden" } return { value = {codigo: "ACESSO_NEGADO", mensagem: "Exame fora do escopo permitido."} } } }
    conditional { if (($bruto.situacao|is_text) == false || (($bruto.situacao != "Realizado") && ($bruto.situacao != "Resultado disponível") && ($bruto.situacao != "Cancelado") && ($bruto.situacao != "Não realizado"))) { util.set_header { value = "HTTP/1.1 400 Bad Request" } return { value = {codigo: "DADOS_INVALIDOS", mensagem: "Situação de Exame inválida."} } } }
    db.edit exame { field_name = "id" field_value = $exame.id data = {situacao: $bruto.situacao, resultado: $bruto|get:"resultado", realizado_em: $bruto|get:"realizado_em", observacoes: $bruto|get:"observacoes"} } as $atualizado
  }
  response = {exame: $atualizado}
  history = false
}
