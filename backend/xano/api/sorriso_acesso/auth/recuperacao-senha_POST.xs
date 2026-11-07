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
        var $otp_text {
          value = $otp|to_text
        }
        var $duracao_minutos {
          value = $duracao / 60
        }
        var $sendgrid_body {
          value = {}
            |set:"subject":"Redefinição de senha · Sorriso+"
            |set:"from":({}|set:"email":$env.workspace.sendgrid_from_email)
            |set:"content":([]
              |push:({}|set:"type":"text/plain"|set:"value":("Redefinição de senha Sorriso+\n\nRecebemos uma solicitação para redefinir sua senha. Utilize o código abaixo para continuar.\n\nCódigo: %s\nEste código é válido por %s minutos.\n\nNão solicitou a redefinição? Ignore este e-mail. Sua senha permanecerá a mesma.\n\nSorriso+\nEsta é uma mensagem automática. Por favor, não responda."|sprintf:$otp_text:$duracao_minutos))
              |push:({}|set:"type":"text/html"|set:"value":("<!doctype html><html lang='pt-BR'><body style='margin:0;padding:0;background:#eef2f1;font-family:Arial,Helvetica,sans-serif;color:#17322b'><table role='presentation' width='100%%' cellspacing='0' cellpadding='0' border='0' style='background:#eef2f1'><tr><td align='center' style='padding:24px 10px'><table role='presentation' width='100%%' cellspacing='0' cellpadding='0' border='0' style='max-width:600px;background:#ffffff'><tr><td style='padding:18px 24px;background:#07543f'><table role='presentation' width='100%%' cellspacing='0' cellpadding='0' border='0'><tr><td width='120' valign='middle'><img src='https://raw.githubusercontent.com/Viana-vv/Odonty/1997d30443ffe2839bd407e2a5ae733d876ee83b/assets/mascote-sorriso-email.png' alt='Mascote Sorriso+' width='96' style='display:block;width:96px;height:auto;border:0'></td><td valign='middle' style='font-size:25px;font-weight:700;color:#ffffff'>Sorriso<span style='color:#8de0bd'>+</span></td></tr></table></td></tr><tr><td style='padding:34px 28px 28px'><div style='font-size:26px;line-height:1;margin-bottom:18px;color:#0a8f68' aria-hidden='true'>&#128274;</div><h1 style='margin:0 0 12px;font-size:26px;line-height:1.25;color:#17322b'>Redefinição de senha</h1><p style='margin:0 0 24px;font-size:16px;line-height:1.55;color:#557169'>Recebemos uma solicitação para redefinir sua senha. Utilize o código abaixo para continuar.</p><table role='presentation' cellspacing='0' cellpadding='0' border='0' style='margin:0 auto'><tr><td style='padding:0 2px'><div style='width:34px;height:34px;line-height:34px;text-align:center;background:#dff7ec;border:1px solid #b9e7d2;color:#07543f;font-size:25px;font-weight:700'>%s</div></td><td style='padding:0 2px'><div style='width:34px;height:34px;line-height:34px;text-align:center;background:#dff7ec;border:1px solid #b9e7d2;color:#07543f;font-size:25px;font-weight:700'>%s</div></td><td style='padding:0 2px'><div style='width:34px;height:34px;line-height:34px;text-align:center;background:#dff7ec;border:1px solid #b9e7d2;color:#07543f;font-size:25px;font-weight:700'>%s</div></td><td style='padding:0 2px'><div style='width:34px;height:34px;line-height:34px;text-align:center;background:#dff7ec;border:1px solid #b9e7d2;color:#07543f;font-size:25px;font-weight:700'>%s</div></td><td style='padding:0 2px'><div style='width:34px;height:34px;line-height:34px;text-align:center;background:#dff7ec;border:1px solid #b9e7d2;color:#07543f;font-size:25px;font-weight:700'>%s</div></td><td style='padding:0 2px'><div style='width:34px;height:34px;line-height:34px;text-align:center;background:#dff7ec;border:1px solid #b9e7d2;color:#07543f;font-size:25px;font-weight:700'>%s</div></td></tr></table><p style='margin:18px 0 0;text-align:center;font-size:13px;color:#557169'>Código para copiar: <strong style='color:#07543f;letter-spacing:2px'>%s</strong></p><p style='margin:20px 0 0;text-align:center;font-size:14px;line-height:1.5;color:#557169'>Este código é válido por %s minutos.</p><table role='presentation' width='100%%' cellspacing='0' cellpadding='0' border='0' style='margin-top:26px;background:#f3faf7'><tr><td width='34' valign='top' style='padding:14px 0 14px 14px;font-size:20px;color:#0a8f68' aria-hidden='true'>&#128737;</td><td style='padding:14px 14px 14px 8px;font-size:13px;line-height:1.5;color:#557169'><strong style='color:#17322b'>Não solicitou a redefinição?</strong><br>Ignore este e-mail. Sua senha permanecerá a mesma.</td></tr></table></td></tr><tr><td style='padding:18px 28px;background:#f7faf9;text-align:center;color:#71837c;font-size:12px;line-height:1.5'>Sorriso+<br>Esta é uma mensagem automática. Por favor, não responda.</td></tr></table></td></tr></table></body></html>"|sprintf:($otp_text|substr:0:1):($otp_text|substr:1:1):($otp_text|substr:2:1):($otp_text|substr:3:1):($otp_text|substr:4:1):($otp_text|substr:5:1):$otp_text:$duracao_minutos))
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
