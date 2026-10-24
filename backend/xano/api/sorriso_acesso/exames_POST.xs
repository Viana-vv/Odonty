// Solicita Exame apenas por Profissional ativo com vínculo Consulta/Paciente.
query "exames" verb=POST {
  api_group = "Sorriso Acesso"
  auth = "conta_acesso"
  input { }
  stack {
    function.run sorriso_validar_sessao { input = {conta_id: $auth.id, sessao_id: $auth.extras.sessao_id} } as $sessao
    util.get_raw_input { encoding = "json" } as $bruto
    db.get conta_acesso { field_name = "id" field_value = $auth.id output = ["id", "perfis", "situacao"] } as $conta
    conditional { if ($conta == null || $conta.situacao != "ativo" || (($conta.perfis|includes:"profissional") == false)) { util.set_header { value = "HTTP/1.1 403 Forbidden" } return { value = {codigo: "ACESSO_NEGADO", mensagem: "Somente Profissional autorizado pode solicitar Exames."} } } }
    db.get profissional { field_name = "conta_acesso_id" field_value = $auth.id output = ["id", "situacao"] } as $profissional
    db.get paciente { field_name = "id" field_value = $bruto.paciente_id output = ["id", "situacao"] } as $paciente
    db.get consulta { field_name = "id" field_value = $bruto.consulta_id output = ["id", "paciente_id", "profissional_id"] } as $consulta
    conditional { if ($profissional == null || $profissional.situacao != "Ativo" || $paciente == null || $paciente.situacao != "ativo" || $consulta == null || $consulta.paciente_id != $paciente.id || $consulta.profissional_id != $profissional.id || ($bruto.tipo|is_text) == false || ($bruto.tipo|trim|strlen) == 0) { util.set_header { value = "HTTP/1.1 400 Bad Request" } return { value = {codigo: "DADOS_INVALIDOS", mensagem: "Confira os dados do Exame."} } } }
    db.add exame { data = {paciente_id: $paciente.id, consulta_id: $consulta.id, profissional_id: $profissional.id, tipo: $bruto.tipo|trim, situacao: "Solicitado", solicitado_em: $bruto.solicitado_em, observacoes: $bruto|get:"observacoes", criado_em: now} } as $exame
    util.set_header { value = "HTTP/1.1 201 Created" }
  }
  response = {exame: {id: $exame.id, paciente_id: $exame.paciente_id, consulta_id: $exame.consulta_id, profissional_id: $exame.profissional_id, tipo: $exame.tipo, situacao: $exame.situacao, solicitado_em: $exame.solicitado_em, realizado_em: null, resultado: null, observacoes: $exame.observacoes}}
  history = false
}
