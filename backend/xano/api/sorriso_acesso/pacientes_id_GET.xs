// Dados cadastrais mÃ­nimos para ediÃ§Ã£o administrativa; sem observacoes ou historico.
query "pacientes/{id}" verb=GET {
  api_group = "Sorriso Acesso"
  auth = "conta_acesso"
  input {
    int id
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
      if ($solicitante == null || $solicitante.situacao != "ativo" || ($solicitante.perfis|intersect:["administrador", "recepcionista"]|count) == 0) {
        util.set_header { value = "HTTP/1.1 403 Forbidden" }
        return { value = {codigo: "ACESSO_NEGADO", mensagem: "Consulta cadastral permitida somente Ã  equipe autorizada."} }
      }
    }
    conditional {
      if ($input.id <= 0) {
        util.set_header { value = "HTTP/1.1 400 Bad Request" }
        return { value = {codigo: "DADOS_INVALIDOS", mensagem: "Identificador de Paciente invÃ¡lido."} }
      }
    }
    db.get paciente {
      field_name = "id"
      field_value = $input.id
      output = ["id", "nome", "data_nascimento", "cpf", "telefone", "celular", "email"]
    } as $paciente
    conditional {
      if ($paciente == null) {
        util.set_header { value = "HTTP/1.1 404 Not Found" }
        return { value = {codigo: "RECURSO_NAO_ENCONTRADO", mensagem: "Paciente nÃ£o encontrado."} }
      }
    }
  }
  response = {paciente: {id: $paciente.id, nome: $paciente.nome, data_nascimento: $paciente.data_nascimento, cpf: ($paciente.cpf|default:""), telefone: $paciente.telefone, celular: ($paciente.celular|default:""), email: ($paciente.email|default:"")}}
  history = false
}
