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
            |set:"subject":"Seu código de acesso · Sorriso+"
            |set:"from":({}|set:"email":$env.workspace.sendgrid_from_email)
            |set:"content":([]
              |push:({}|set:"type":"text/plain"|set:"value":("Seu código Sorriso+ é: %s. Ele expira em 10 minutos e só pode ser usado uma vez."|sprintf:$otp))
              |push:({}|set:"type":"text/html"|set:"value":("<!doctype html><html><body style='margin:0;background:#f4faf7;font-family:Arial,Helvetica,sans-serif;color:#17322b'><table role='presentation' width='100%%' cellspacing='0' cellpadding='0' style='padding:32px 12px;background:#f4faf7'><tr><td align='center'><table role='presentation' width='100%%' cellspacing='0' cellpadding='0' style='max-width:560px;background:#ffffff;border:1px solid #dcebe5;border-radius:18px;overflow:hidden'><tr><td style='padding:28px 32px;background:#00694e;text-align:center'><img src='https://raw.githubusercontent.com/Viana-vv/Odonty/main/assets/mascote-sorriso.png' alt='Sorriso+' width='120' style='display:block;margin:0 auto 12px;max-width:120px;height:auto'><div style='font-size:24px;font-weight:700;color:#ffffff'>Sorriso+</div></td></tr><tr><td style='padding:32px'><h1 style='margin:0 0 12px;font-size:24px;color:#17322b'>Confirme seu acesso</h1><p style='margin:0 0 22px;font-size:16px;line-height:1.5;color:#557169'>Recebemos uma solicitação para redefinir sua senha. Use o código abaixo para continuar:</p><div style='padding:18px;text-align:center;background:#e2f8ef;border:1px solid #b8e8d2;border-radius:12px;font-size:34px;letter-spacing:8px;font-weight:700;color:#00694e'>%s</div><p style='margin:22px 0 0;font-size:14px;line-height:1.5;color:#6b7f78'>Este código expira em 10 minutos e só pode ser usado uma vez. Se você não solicitou a recuperação, ignore este e-mail.</p></td></tr><tr><td style='padding:18px 32px;background:#f7fbf9;color:#71837c;font-size:12px;text-align:center'>Cuidado que transforma sorrisos.</td></tr></table></td></tr></table></body></html>"|sprintf:$otp))
            )
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
