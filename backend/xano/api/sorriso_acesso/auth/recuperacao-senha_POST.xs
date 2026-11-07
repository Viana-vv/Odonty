// Solicita código. A resposta é neutra para não revelar contas existentes.
query "auth/recuperacao-senha" verb=POST {
  api_group = "Sorriso Acesso"
  input {
    email email filters=trim|lower
  }
  stack {
    util.set_header {
      value = "Cache-Control: no-store"
      duplicates = "replace"
    }
    var $duracao {
      value = $env|get:"PASSWORD_OTP_TTL_SECONDS":600|to_int
    }
    precondition ($duracao >= 60 && $duracao <= 900) {
      error_type = "standard"
      error = "Configuração de OTP inválida."
    }
    security.create_uuid as $operacao
    security.random_number {
      min = 100000
      max = 999999
    } as $otp
    db.get conta_acesso {
      field_name = "email"
      field_value = $input.email
      output = ["id", "email", "nome", "situacao"]
    } as $conta
    conditional {
      if ($conta != null && $conta.situacao == "ativo") {
        db.add recuperacao_senha {
          data = {
            operacao_id: $operacao
            email      : $input.email
            otp_hash   : $otp|to_text
            expira_em  : now|add_secs_to_timestamp:$duracao
            tentativas : 0
            validado   : false
            utilizado  : false
          }
        } as $registro
        var $sendgrid_body {
          value = {}
            |set:"subject":"Código de recuperação Sorriso+"
            |set:"from":({}|set:"email":$env.workspace.sendgrid_from_email)
            |set:"content":([]|push:({}|set:"type":"text/plain"|set:"value":$otp|to_text))
            |set:"personalizations":([]|push:({}|set:"to":([]|push:({}|set:"email":$conta.email))))
        }
        var $sendgrid_auth {
          value = "Authorization: Bearer %s"|sprintf:$env.workspace.sendgrid_api_key
        }
        api.request {
          url = "https://api.sendgrid.com/v3/mail/send"
          method = "POST"
          params = $sendgrid_body
          headers = []|push:"Content-Type: application/json"|push:$sendgrid_auth
          timeout = 30
        } as $envio
        conditional {
          if ($envio.response.status != 202) {
            util.set_header {
              value = "HTTP/1.1 503 Service Unavailable"
              duplicates = "replace"
            }
            return {
              value = {codigo: "SERVICO_INDISPONIVEL", mensagem: "Não foi possível enviar o código agora."}
            }
          }
        }
      }
    }
  }
  response = {operacao_id: $operacao}
  history = false
  guid = "cbiuOUYN4qoEx4mKeokJGJ5kxPA"
}
