query "exames/{exame_id}/situacao" verb=PATCH {
  api_group = "Sorriso Acesso"
  auth = "conta_acesso"
  input {
    int exame_id
    enum situacao {
      values = ["Realizado", "Resultado disponível", "Cancelado", "Não realizado"]
    }
    text resultado?
    timestamp realizado_em?
    text observacoes?
  }
  stack {
    function.run sorriso_validar_sessao {
      input = {conta_id: $auth.id, sessao_id: $auth.extras.sessao_id}
    } as $sessao
    db.get profissional {
      field_name = "conta_acesso_id"
      field_value = $auth.id
      output = ["id", "situacao"]
    } as $profissional
    db.get exame {
      field_name = "id"
      field_value = $input.exame_id
      output = ["id", "profissional_id"]
    } as $exame
    conditional {
      if ($profissional == null || $profissional.situacao != "Ativo" || $exame == null || $exame.profissional_id != $profissional.id) {
        util.set_header {
          value = "HTTP/1.1 403 Forbidden"
        }
        return {
          value = {codigo: "ACESSO_NEGADO", mensagem: "Exame fora do escopo permitido."}
        }
      }
    }
    db.edit exame {
      field_name = "id"
      field_value = $input.exame_id
      data = {situacao: $input.situacao, resultado: $input.resultado, realizado_em: $input.realizado_em, observacoes: $input.observacoes}
    } as $atualizado
  }
  response = {exame: $atualizado}
  history = false
}
