// Valida vínculo e validade da sessão; logout permite sessão revogada.
function sorriso_validar_sessao {
  input {
    int conta_id
    text sessao_id
    bool encerrar?=false
  }
  stack {
    db.get sessao_acesso {
      field_name = "id"
      field_value = $input.sessao_id
    } as $sessao
    precondition ($sessao != null) {
      error_type = "unauthorized"
      error = "Sessão inválida."
    }
    precondition ($sessao.conta_acesso_id == $input.conta_id && $sessao.expira_em > now) {
      error_type = "unauthorized"
      error = "Sessão inválida."
    }
    conditional {
      if ($input.encerrar == false) {
        precondition ($sessao.revogada_em == null) {
          error_type = "unauthorized"
          error = "Sessão inválida."
        }
      }
    }
  }
  response = $sessao
  history = false
  guid = "BoxCc5Nin3a8XvLlgAnTwL3jtIY"
}

