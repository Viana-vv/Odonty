// Atualiza somente dados cadastrais autorizados de um Paciente existente.
query "pacientes/{id}" verb=PATCH {
  api_group = "Sorriso Acesso"
  auth = "conta_acesso"
  input {
    int id
  }
  stack {
    util.set_header { value = "Cache-Control: no-store" duplicates = "replace" }
    function.run sorriso_validar_sessao {
      input = {conta_id: $auth.id, sessao_id: $auth.extras.sessao_id}
    } as $sessao
    db.get conta_acesso {
      field_name = "id"
      field_value = $auth.id
      output = ["id", "perfis", "situacao"]
    } as $solicitante
    conditional {
      if ($solicitante == null || $solicitante.situacao != "ativo" || ($solicitante.perfis|intersect:["administrador", "recepcionista"]|count) == 0) {
        util.set_header { value = "HTTP/1.1 403 Forbidden" }
        return { value = {codigo: "ACESSO_NEGADO", mensagem: "EdiÃ§Ã£o permitida somente Ã  equipe autorizada."} }
      }
    }
    conditional {
      if ($input.id <= 0) {
        util.set_header { value = "HTTP/1.1 400 Bad Request" }
        return { value = {codigo: "DADOS_INVALIDOS", mensagem: "Identificador de Paciente invÃ¡lido."} }
      }
    }
    db.get paciente {
      field_name = "id"
      field_value = $input.id
      output = ["id"]
    } as $existente
    conditional {
      if ($existente == null) {
        util.set_header { value = "HTTP/1.1 404 Not Found" }
        return { value = {codigo: "RECURSO_NAO_ENCONTRADO", mensagem: "Paciente nÃ£o encontrado."} }
      }
    }
    try_catch {
      try {
        util.get_raw_input { encoding = "json" } as $bruto
      }
      catch {
        util.set_header { value = "HTTP/1.1 400 Bad Request" }
        return { value = {codigo: "DADOS_INVALIDOS", mensagem: "Confira os dados informados."} }
      }
    }
    conditional {
      if (($bruto|is_object) == false) {
        util.set_header { value = "HTTP/1.1 400 Bad Request" }
        return { value = {codigo: "DADOS_INVALIDOS", mensagem: "Confira os dados informados."} }
      }
    }
    var $campo_invalido { value = false }
    foreach ($bruto|keys) {
      each as $chave {
        conditional {
          if ($chave != "nome" && $chave != "data_nascimento" && $chave != "telefone" && $chave != "cpf" && $chave != "email" && $chave != "celular") {
            var.update $campo_invalido { value = true }
          }
        }
      }
    }
    conditional {
      if (($bruto|is_object) == false || $campo_invalido || ($bruto|keys|count) != 6 || ($bruto|get:"nome"|is_text) == false || ($bruto|get:"data_nascimento"|is_text) == false || ($bruto|get:"telefone"|is_text) == false || ($bruto|get:"cpf"|is_text) == false || ($bruto|get:"email"|is_text) == false || ($bruto|get:"celular"|is_text) == false) {
        util.set_header { value = "HTTP/1.1 400 Bad Request" }
        return { value = {codigo: "DADOS_INVALIDOS", mensagem: "Preencha todos os campos cadastrais permitidos."} }
      }
    }
    var $nome { value = $bruto.nome|trim }
    var $email { value = $bruto.email|trim|to_lower }
    var $telefone { value = $bruto.telefone|trim|replace:"(":""|replace:")":""|replace:"-":""|replace:" ":"" }
    var $celular { value = $bruto.celular|trim|replace:"(":""|replace:")":""|replace:"-":""|replace:" ":"" }
    var $cpf_entrada { value = $bruto.cpf|trim }
    var $cpf { value = $cpf_entrada|replace:".":""|replace:"-":"" }
    var $data_nascimento { value = $bruto.data_nascimento|trim }
    conditional {
      if (($nome|strlen) < 2 || ($nome|strlen) > 120 || ($email|strlen) > 254 || ("/^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/"|regex_test:$email) == false || ("/^[0-9]{10,11}$/"|regex_test:$telefone) == false || ("/^[0-9]{10,11}$/"|regex_test:$celular) == false || ("/^[0-9]{11}$/"|regex_test:$cpf) == false || ("/^(?:[0-9]{11}|[0-9]{3}\\.[0-9]{3}\\.[0-9]{3}-[0-9]{2})$/"|regex_test:$cpf_entrada) == false || ("/^[0-9]{4}-[0-9]{2}-[0-9]{2}$/"|regex_test:$data_nascimento) == false) {
        util.set_header { value = "HTTP/1.1 400 Bad Request" }
        return { value = {codigo: "DADOS_INVALIDOS", mensagem: "Confira os dados cadastrais informados."} }
      }
    }
    conditional {
      if (("/^([0-9])\\1{10}$/"|regex_test:$cpf) == true) {
        util.set_header { value = "HTTP/1.1 400 Bad Request" }
        return { value = {codigo: "DADOS_INVALIDOS", mensagem: "Confira os dados cadastrais informados."} }
      }
    }
    foreach ([9, 10]) {
      each as tamanho {
        var $soma { value = 0 }
        for ($tamanho) {
          each as indice {
            var.update $soma { value = $soma + (($cpf|substr:$indice:1|to_int) * ($tamanho + 1 - $indice)) }
          }
        }
        var $resto { value = $soma|modulus:11 }
        var $verificador { value = 0 }
        conditional {
          if ($resto >= 2) { var.update $verificador { value = 11 - $resto } }
        }
        conditional {
          if (($cpf|substr:$tamanho:1|to_int) != $verificador) {
            util.set_header { value = "HTTP/1.1 400 Bad Request" }
            return { value = {codigo: "DADOS_INVALIDOS", mensagem: "Confira os dados cadastrais informados."} }
          }
        }
      }
    }
    var $ano { value = $data_nascimento|substr:0:4|to_int }
    var $mes { value = $data_nascimento|substr:5:2|to_int }
    var $dia { value = $data_nascimento|substr:8:2|to_int }
    var $dias_mes { value = 31 }
    conditional {
      if (($mes == 4) || ($mes == 6) || ($mes == 9) || ($mes == 11)) { var.update $dias_mes { value = 30 } }
      elseif ($mes == 2) {
        var.update $dias_mes { value = 28 }
        conditional {
          if (($ano|modulus:400) == 0 || (($ano|modulus:4) == 0 && ($ano|modulus:100) != 0)) { var.update $dias_mes { value = 29 } }
        }
      }
    }
    var $hoje { value = now|format_timestamp:"Ymd":"America/Sao_Paulo"|to_int }
    var $nascimento_ordenado { value = ($ano * 10000) + ($mes * 100) + $dia }
    conditional {
      if ($ano < 1 || $mes < 1 || $mes > 12 || $dia < 1 || $dia > $dias_mes || $nascimento_ordenado > $hoje) {
        util.set_header { value = "HTTP/1.1 400 Bad Request" }
        return { value = {codigo: "DADOS_INVALIDOS", mensagem: "Informe uma data de nascimento vÃ¡lida e nÃ£o futura."} }
      }
    }
    db.query paciente {
      where = $db.paciente.id != $input.id && $db.paciente.cpf == $cpf
      return = {type: "single"}
      output = ["id"]
    } as $cpf_existente
    conditional {
      if ($cpf_existente != null) {
        util.set_header { value = "HTTP/1.1 409 Conflict" }
        return { value = {codigo: "CPF_DUPLICADO", mensagem: "CPF jÃ¡ cadastrado."} }
      }
    }
    var $atualizado { value = null }
    try_catch {
      try {
        db.edit paciente {
          field_name = "id"
          field_value = $input.id
          data = {nome: $nome, data_nascimento: $data_nascimento, telefone: $telefone, cpf: $cpf, email: $email, celular: $celular, atualizado_em: now}
        } as $atualizado
      }
      catch {
        var.update $atualizado { value = null }
      }
    }
    conditional {
      if ($atualizado == null) {
        db.query paciente {
          where = $db.paciente.id != $input.id && $db.paciente.cpf == $cpf
          return = {type: "single"}
          output = ["id"]
        } as $cpf_concorrente
        conditional {
          if ($cpf_concorrente != null) {
            util.set_header { value = "HTTP/1.1 409 Conflict" }
            return { value = {codigo: "CPF_DUPLICADO", mensagem: "CPF jÃ¡ cadastrado."} }
          }
        }
        util.set_header { value = "HTTP/1.1 503 Service Unavailable" }
        return { value = {codigo: "SERVICO_INDISPONIVEL", mensagem: "NÃ£o foi possÃ­vel confirmar a atualizaÃ§Ã£o."} }
      }
    }
  }
  response = {paciente: {id: $atualizado.id, nome: $atualizado.nome, data_nascimento: $atualizado.data_nascimento, cpf: $atualizado.cpf, telefone: $atualizado.telefone, celular: $atualizado.celular, email: $atualizado.email}}
  history = false
}
