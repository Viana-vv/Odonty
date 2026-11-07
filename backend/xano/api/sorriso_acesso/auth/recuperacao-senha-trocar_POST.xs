query "auth/recuperacao-senha/trocar" verb=POST {
  api_group = "Sorriso Acesso"
  input {
    text operacao_id filters=trim
    text senha filters=min:1
  }
  stack {
    util.set_header {
      value = "Cache-Control: no-store"
      duplicates = "replace"
    }
    precondition (($input.senha|strlen) >= 12 && ($input.senha|strlen) <= 128) {
      error_type = "standard"
      error = "A senha deve ter entre 12 e 128 caracteres."
    }
    db.get recuperacao_senha {
      field_name = "operacao_id"
      field_value = $input.operacao_id
    } as $registro
    conditional {
      if ($registro == null || $registro.utilizado != false || $registro.validado != true || $registro.expira_em <= now) {
        util.set_header {
          value = "HTTP/1.1 400 Bad Request"
          duplicates = "replace"
        }
        return {
          value = {codigo: "OTP_INVALIDO", mensagem: "Código inválido ou expirado."}
        }
      }
    }
    db.get conta_acesso {
      field_name = "email"
      field_value = $registro.email
    } as $conta
    conditional {
      if ($conta == null || $conta.situacao != "ativo") {
        util.set_header {
          value = "HTTP/1.1 400 Bad Request"
          duplicates = "replace"
        }
        return {
          value = {codigo: "OTP_INVALIDO", mensagem: "Código inválido ou expirado."}
        }
      }
    }
    db.edit conta_acesso {
      field_name = "id"
      field_value = $conta.id
      data = {senha: $input.senha}
    }
    db.edit recuperacao_senha {
      field_name = "id"
      field_value = $registro.id
      data = {utilizado: true}
    }
  }
  response = {alterada: true}
  history = false
  guid = "ANOS4Ts4KOJkKe2KPs8T_fYeLLs"
}
