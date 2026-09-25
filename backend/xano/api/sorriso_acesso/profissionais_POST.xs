// Cria Profissional e Conta de Acesso na mesma transacao, sem registrar senhas.
query profissionais verb=POST {
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
    util.get_raw_input { encoding = "json" } as $bruto
    conditional {
      if (($bruto|is_object) == false) {
        util.set_header { value = "HTTP/1.1 400 Bad Request" }
        return { value = {codigo: "DADOS_INVALIDOS", mensagem: "Confira os dados do profissional."} }
      }
    }
    conditional {
      if (($bruto|keys|count) != 5 || ($bruto|get:"nome"|is_text) == false || ($bruto|get:"email"|is_text) == false || ($bruto|get:"senha"|is_text) == false || ($bruto|get:"cro"|is_text) == false || ($bruto|get:"especialidade_id"|is_int) == false) {
        util.set_header { value = "HTTP/1.1 400 Bad Request" }
        return { value = {codigo: "DADOS_INVALIDOS", mensagem: "Confira os dados do profissional."} }
      }
    }
    var $nome { value = $bruto.nome|trim }
    var $email { value = $bruto.email|trim|to_lower }
    var $cro_entrada { value = $bruto.cro|trim|to_upper }
    conditional {
      if (($nome|strlen) < 2 || ($nome|strlen) > 120 || ($email|strlen) > 254 || ($email|regex_test:"^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$") == false || ($bruto.senha|strlen) < 12 || ($bruto.senha|strlen) > 128 || ($cro_entrada|strlen) > 32 || ($cro_entrada|regex_test:"^(AC|AL|AP|AM|BA|CE|DF|ES|GO|MA|MT|MS|MG|PA|PB|PR|PE|PI|RJ|RN|RS|RO|RR|SC|SP|SE|TO)-[0-9]{1,10}$") == false || $bruto.especialidade_id <= 0) {
        util.set_header { value = "HTTP/1.1 400 Bad Request" }
        return { value = {codigo: "DADOS_INVALIDOS", mensagem: "Confira os dados do profissional."} }
      }
    }
    var $numero { value = $cro_entrada|split:"-"|get:1|to_int }
    conditional {
      if ($numero <= 0) {
        util.set_header { value = "HTTP/1.1 400 Bad Request" }
        return { value = {codigo: "DADOS_INVALIDOS", mensagem: "Confira os dados do profissional."} }
      }
    }
    var $cro { value = ($cro_entrada|split:"-"|get:0) ~ "-" ~ ($numero|to_text) }
    db.get especialidade {
      field_name = "id"
      field_value = $bruto.especialidade_id
      output = ["id", "nome", "ativo"]
    } as $especialidade
    conditional {
      if ($especialidade == null || $especialidade.ativo == false) {
        util.set_header { value = "HTTP/1.1 400 Bad Request" }
        return { value = {codigo: "DADOS_INVALIDOS", mensagem: "Confira os dados do profissional."} }
      }
    }
    db.get conta_acesso {
      field_name = "email"
      field_value = $email
      output = ["id"]
    } as $duplicada_conta
    db.get profissional {
      field_name = "cro"
      field_value = $cro
      output = ["id"]
    } as $duplicado_profissional
    conditional {
      if ($duplicada_conta != null || $duplicado_profissional != null) {
        util.set_header { value = "HTTP/1.1 409 Conflict" }
        return { value = {codigo: "CADASTRO_DUPLICADO", mensagem: "E-mail ou CRO já cadastrado."} }
      }
    }
    try_catch {
      try {
        db.transaction {
          stack {
            db.add conta_acesso {
              data = {nome: $nome, email: $email, senha: $bruto.senha, perfis: ["profissional"], situacao: "ativo"}
            } as $nova_conta
            db.add profissional {
              data = {nome: $nome, cro: $cro, email: $email, especialidade_id: $especialidade.id, situacao: "Ativo", conta_acesso_id: $nova_conta.id, atualizado_em: now}
            } as $novo_profissional
          }
        }
      }
      catch {
        // Reconsulta apenas chaves apos rollback; nunca devolve o erro bruto.
        db.get conta_acesso {
          field_name = "email"
          field_value = $email
          output = ["id"]
        } as $conflito_conta
        db.get profissional {
          field_name = "cro"
          field_value = $cro
          output = ["id"]
        } as $conflito_profissional
        conditional {
          if ($conflito_conta != null || $conflito_profissional != null) {
        util.set_header { value = "HTTP/1.1 409 Conflict" }
        return { value = {codigo: "CADASTRO_DUPLICADO", mensagem: "E-mail ou CRO já cadastrado."} }
          }
        }
        util.set_header { value = "HTTP/1.1 503 Service Unavailable" }
        return { value = {codigo: "SERVICO_INDISPONIVEL", mensagem: "Não foi possível confirmar o cadastro."} }
      }
    }
    util.set_header { value = "HTTP/1.1 201 Created" }
  }
  response = {
    profissional: {id: $novo_profissional.id, nome: $novo_profissional.nome, cro: $novo_profissional.cro, especialidade: {id: $especialidade.id, nome: $especialidade.nome}, situacao: "ativo"}
    conta: {id: $nova_conta.id, perfis: ["profissional"], situacao: "ativo"}
  }
  history = false
  guid = "U-m9c1XyBrsJQTtMxtnkDNfwR2U"
}
