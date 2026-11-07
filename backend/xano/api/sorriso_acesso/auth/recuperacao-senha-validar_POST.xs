query "auth/recuperacao-senha/validar" verb=POST {
  api_group = "Sorriso Acesso"
  input {
    text operacao_id filters=trim
    text otp filters=trim
  }
  stack {
    util.set_header { value = "Cache-Control: no-store" duplicates = "replace" }
    db.get recuperacao_senha {
      field_name = "operacao_id"
      field_value = $input.operacao_id
    } as $registro
    conditional {
      if ($registro == null || $registro.utilizado == true || $registro.validado == true || $registro.expira_em <= now || $registro.tentativas >= 5) {
        util.set_header { value = "HTTP/1.1 400 Bad Request" duplicates = "replace" }
        return { value = {codigo: "OTP_INVALIDO", mensagem: "Código inválido ou expirado."} }
      }
    }
    security.check_password {
      text_password = $input.otp
      hash_password = $registro.otp_hash
    } as $correto
    conditional {
      if ($correto == false) {
        db.edit recuperacao_senha {
          field_name = "id"
          field_value = $registro.id
          data = {tentativas: $registro.tentativas + 1}
        }
        util.set_header { value = "HTTP/1.1 400 Bad Request" duplicates = "replace" }
        return { value = {codigo: "OTP_INVALIDO", mensagem: "Código inválido ou expirado."} }
      }
    }
    db.edit recuperacao_senha {
      field_name = "id"
      field_value = $registro.id
      data = {validado: true}
    }
  }
  response = {validado: true}
  history = false
  guid = "5p0Ttj8S4M8B3Z5SV3kxZn_l27M"
}
