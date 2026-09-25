// Autentica Conta de Acesso ativa sem registrar credenciais.
query "auth/login" verb=POST {
  api_group = "Sorriso Acesso"
  input {
    email email filters=trim|lower
    text senha filters=min:1
  }
  stack {
    util.set_header { value = "Cache-Control: no-store" }
    util.get_raw_input { encoding = "json" } as $bruto
    conditional {
      if (($bruto|keys|count) != 2) {
        util.set_header { value = "HTTP/1.1 400 Bad Request" }
        return { value = {codigo: "DADOS_INVALIDOS", mensagem: "Informe somente e-mail e senha."} }
      }
    }
    db.get conta_acesso {
      field_name = "email"
      field_value = $input.email
    } as $conta
    conditional {
      if ($conta == null) {
        util.set_header { value = "HTTP/1.1 401 Unauthorized" }
        return { value = {codigo: "CREDENCIAIS_INVALIDAS", mensagem: "Credenciais inválidas ou conta indisponível."} }
      }
    }
    security.check_password {
      text_password = $input.senha
      hash_password = $conta.senha
    } as $senha_valida
    conditional {
      if ($senha_valida == false || $conta.situacao != "ativo") {
        util.set_header { value = "HTTP/1.1 401 Unauthorized" }
        return { value = {codigo: "CREDENCIAIS_INVALIDAS", mensagem: "Credenciais inválidas ou conta indisponível."} }
      }
    }
    conditional {
      if (($conta.perfis|intersect:["administrador", "recepcionista", "profissional"]|count) == 0) {
        util.set_header { value = "HTTP/1.1 403 Forbidden" }
        return { value = {codigo: "ACESSO_NEGADO", mensagem: "Acesso não permitido."} }
      }
    }
    var $duracao { value = $env|get:"AUTH_SESSION_TTL_SECONDS":3600|to_int }
    precondition ($duracao > 0 && $duracao <= 3600) {
      error_type = "standard"
      error = "Configuração de sessão inválida."
    }
    var $prazo { value = now|add_secs_to_timestamp:$duracao }
    security.create_uuid as $sessao_id
    db.transaction {
      stack {
        db.add sessao_acesso {
          data = {id: $sessao_id, conta_acesso_id: $conta.id, criada_em: now, expira_em: $prazo, revogada_em: null}
        } as $sessao
        security.create_auth_token {
          table = "conta_acesso"
          id = $conta.id
          extras = {sessao_id: $sessao_id}
          expiration = $duracao
        } as $token
      }
    }
  }
  response = {token: $token, tipo_token: "Bearer", expira_em: $prazo|format_timestamp:"c":"UTC"}
  history = false
  guid = "gWVt7OY1TQ9AZ0705k_lApm1nT4"
}


