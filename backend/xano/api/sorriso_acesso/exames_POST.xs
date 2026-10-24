query "exames" verb=POST {
  api_group = "Sorriso Acesso"
  auth = "conta_acesso"
  input {
    int paciente_id
    int consulta_id
    text tipo
    timestamp solicitado_em
    text observacoes?
  }
  stack {
    function.run sorriso_validar_sessao {
      input = {conta_id: $auth.id, sessao_id: $auth.extras.sessao_id}
    } as $sessao
    db.get conta_acesso {
      field_name = "id"
      field_value = $auth.id
      output = ["id", "perfis", "situacao"]
    } as $conta
    conditional {
      if ($conta == null || $conta.situacao != "ativo" || ($conta.perfis|includes:"profissional") == false) {
        util.set_header {
          value = "HTTP/1.1 403 Forbidden"
        }
        return {
          value = {codigo: "ACESSO_NEGADO", mensagem: "Somente Profissional autorizado pode solicitar Exames."}
        }
      }
    }
    db.get profissional {
      field_name = "conta_acesso_id"
      field_value = $auth.id
      output = ["id", "situacao"]
    } as $profissional
    db.get paciente {
      field_name = "id"
      field_value = $input.paciente_id
      output = ["id", "situacao"]
    } as $paciente
    db.get consulta {
      field_name = "id"
      field_value = $input.consulta_id
      output = ["id", "paciente_id", "profissional_id"]
    } as $consulta
    conditional {
      if ($profissional == null || $profissional.situacao != "Ativo" || $paciente == null || $paciente.situacao != "ativo" || $consulta == null || $consulta.paciente_id != $paciente.id || $consulta.profissional_id != $profissional.id) {
        util.set_header {
          value = "HTTP/1.1 400 Bad Request"
        }
        return {
          value = {codigo: "DADOS_INVALIDOS", mensagem: "Confira os dados do Exame."}
        }
      }
    }
    db.add exame {
      data = {paciente_id: $paciente.id, consulta_id: $consulta.id, profissional_id: $profissional.id, tipo: $input.tipo, situacao: "Solicitado", solicitado_em: $input.solicitado_em, observacoes: $input.observacoes, criado_em: now}
    } as $exame
    util.set_header {
      value = "HTTP/1.1 201 Created"
    }
  }
  response = {exame: $exame}
  history = false
}
