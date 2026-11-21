// Cria exclusivamente Conta de Acesso de Recepcionista.
query "contas-acesso/recepcionistas" verb=POST {
  api_group = "Sorriso Acesso"
  auth = "conta_acesso"
  input { }
  stack {
    util.set_header { value = "Cache-Control: no-store" }
    function.run sorriso_validar_sessao {
      input = {conta_id: $auth.id, sessao_id: $auth.extras.sessao_id}
    } as $sessao
    db.get conta_acesso {
      field_name = "id"
      field_value = $auth.id
      output = ["id", "perfis", "situacao"]
    } as $solicitante
    conditional {
      if ($solicitante == null || $solicitante.situacao != "ativo" || ($solicitante.perfis|intersect:["administrador"]|count) == 0) {
        util.set_header { value = "HTTP/1.1 403 Forbidden" }
        return { value = {codigo: "ACESSO_NEGADO", mensagem: "Cadastro permitido somente ao Administrador."} }
      }
    }
    try_catch {
      try {
        util.get_raw_input { encoding = "json" } as $bruto
      }
      catch {
        util.set_header { value = "HTTP/1.1 400 Bad Request" }
        return { value = {codigo: "DADOS_INVALIDOS", mensagem: "Confira os dados da Conta de Acesso."} }
      }
    }
    conditional {
      if (($bruto|is_object) == false) {
        util.set_header { value = "HTTP/1.1 400 Bad Request" }
        return { value = {codigo: "DADOS_INVALIDOS", mensagem: "Confira os dados da Conta de Acesso."} }
      }
    }
    conditional {
      if (($bruto|keys|count) != 3 || ($bruto|get:"nome"|is_text) == false || ($bruto|get:"email"|is_text) == false || ($bruto|get:"senha"|is_text) == false) {
        util.set_header { value = "HTTP/1.1 400 Bad Request" }
        return { value = {codigo: "DADOS_INVALIDOS", mensagem: "Confira os dados da Conta de Acesso."} }
      }
    }
    var $nome { value = $bruto.nome|trim }
    var $email { value = $bruto.email|trim|to_lower }
    conditional {
      if (($nome|strlen) < 2 || ($nome|strlen) > 120 || ($email|strlen) > 254 || ("/^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/"|regex_test:$email) == false || ($bruto.senha|strlen) < 12 || ($bruto.senha|strlen) > 128) {
        util.set_header { value = "HTTP/1.1 400 Bad Request" }
        return { value = {codigo: "DADOS_INVALIDOS", mensagem: "Confira os dados da Conta de Acesso."} }
      }
    }
    db.get conta_acesso {
      field_name = "email"
      field_value = $email
      output = ["id"]
    } as $duplicada
    conditional {
      if ($duplicada != null) {
        util.set_header { value = "HTTP/1.1 409 Conflict" }
        return { value = {codigo: "CADASTRO_DUPLICADO", mensagem: "E-mail já cadastrado."} }
      }
    }

    try_catch {
      try {
        db.add conta_acesso {
          data = {nome: $nome, email: $email, senha: $bruto.senha, perfis: ["recepcionista"], situacao: "ativo"}
        } as $nova_conta
      }
      catch {
        db.get conta_acesso {
          field_name = "email"
          field_value = $email
          output = ["id"]
        } as $conflito
        conditional {
          if ($conflito != null) {
            util.set_header { value = "HTTP/1.1 409 Conflict" }
            return { value = {codigo: "CADASTRO_DUPLICADO", mensagem: "E-mail já cadastrado."} }
          }
        }
        util.set_header { value = "HTTP/1.1 503 Service Unavailable" }
        return { value = {codigo: "SERVICO_INDISPONIVEL", mensagem: "Não foi possível confirmar o cadastro."} }
      }
    }
    util.set_header { value = "HTTP/1.1 201 Created" }
  }
  response = {
    conta: {
      id: $nova_conta.id
      nome: $nova_conta.nome
      email: $nova_conta.email
      perfis: ["recepcionista"]
      situacao: "ativo"
    }
  }
  history = false
  guid = "TYTDQI5ek6-lvPJEnFr8BobxPPQ"
}
