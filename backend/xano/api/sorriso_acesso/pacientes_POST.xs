// Cadastra Paciente e Prontuario sem guardar dados no historico de requisicoes.
query pacientes verb=POST {
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
      if ($solicitante == null || $solicitante.situacao != "ativo" || ($solicitante.perfis|intersect:["administrador", "recepcionista"]|count) == 0) {
        util.set_header { value = "HTTP/1.1 403 Forbidden" }
        return { value = {codigo: "ACESSO_NEGADO", mensagem: "Cadastro permitido somente à equipe autorizada."} }
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
    conditional {
      if (($bruto|is_object) == false || ($bruto|keys|count) != 7 || ($bruto|get:"nome"|is_text) == false || ($bruto|get:"data_nascimento"|is_text) == false || ($bruto|get:"telefone"|is_text) == false || ($bruto|get:"cpf"|is_text) == false || ($bruto|get:"email"|is_text) == false || ($bruto|get:"celular"|is_text) == false || ($bruto|get:"operacao_id"|is_text) == false) {
        util.set_header { value = "HTTP/1.1 400 Bad Request" }
        return { value = {codigo: "DADOS_INVALIDOS", mensagem: "Preencha todos os campos obrigatórios."} }
      }
    }
    var $nome { value = $bruto.nome|trim }
    var $email { value = $bruto.email|trim|to_lower }
    var $telefone { value = $bruto.telefone|trim|replace:"(":""|replace:")":""|replace:"-":""|replace:" ":"" }
    var $celular { value = $bruto.celular|trim|replace:"(":""|replace:")":""|replace:"-":""|replace:" ":"" }
    var $cpf_entrada { value = $bruto.cpf|trim }
    var $cpf { value = $cpf_entrada|replace:".":""|replace:"-":"" }
    var $data_nascimento { value = $bruto.data_nascimento }
    conditional {
      if (($bruto.operacao_id|strlen) != 36) {
        util.set_header { value = "HTTP/1.1 400 Bad Request" }
        return { value = {codigo: "DADOS_INVALIDOS", mensagem: "Confira os dados informados."} }
      }
    }
    conditional {
      if (("/^(?:[0-9]{11}|[0-9]{3}\\.[0-9]{3}\\.[0-9]{3}-[0-9]{2})$/"|regex_test:$cpf_entrada) == false) {
        util.set_header { value = "HTTP/1.1 400 Bad Request" }
        return { value = {codigo: "DADOS_INVALIDOS", mensagem: "Confira os dados informados."} }
      }
    }
    conditional {
      if (($nome|strlen) < 2 || ($nome|strlen) > 120 || ($email|strlen) > 254 || ("/^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/"|regex_test:$email) == false || ("/^[0-9]{10,11}$/"|regex_test:$telefone) == false || ("/^[0-9]{10,11}$/"|regex_test:$celular) == false || ("/^[0-9]{11}$/"|regex_test:$cpf) == false || ("/^[0-9]{4}-[0-9]{2}-[0-9]{2}$/"|regex_test:$data_nascimento) == false || ("/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/"|regex_test:$bruto.operacao_id) == false) {
        util.set_header { value = "HTTP/1.1 400 Bad Request" }
        return { value = {codigo: "DADOS_INVALIDOS", mensagem: "Confira os dados informados."} }
      }
    }
    conditional {
      if (("/^([0-9])\\1{10}$/"|regex_test:$cpf) == true) {
        util.set_header { value = "HTTP/1.1 400 Bad Request" }
        return { value = {codigo: "DADOS_INVALIDOS", mensagem: "Confira os dados informados."} }
      }
    }
    // Os dois verificadores sao calculados independentemente no backend.
    foreach ([9, 10]) {
      each as tamanho {
        var $soma { value = 0 }
        for ($tamanho) {
          each as indice {
            var.update $soma {
              value = $soma + (($cpf|substr:$indice:1|to_int) * ($tamanho + 1 - $indice))
            }
          }
        }
        var $resto { value = $soma|modulus:11 }
        var $verificador { value = 0 }
        conditional {
          if ($resto >= 2) {
            var.update $verificador { value = 11 - $resto }
          }
        }
        conditional {
          if (($cpf|substr:$tamanho:1|to_int) != $verificador) {
            util.set_header { value = "HTTP/1.1 400 Bad Request" }
            return { value = {codigo: "DADOS_INVALIDOS", mensagem: "Confira os dados informados."} }
          }
        }
      }
    }
    // Validacao gregoriana evita aceitar datas que o parser normalizaria.
    var $ano { value = $data_nascimento|substr:0:4|to_int }
    var $mes { value = $data_nascimento|substr:5:2|to_int }
    var $dia { value = $data_nascimento|substr:8:2|to_int }
    var $dias_mes { value = 31 }
    conditional {
      if (($mes == 4) || ($mes == 6) || ($mes == 9) || ($mes == 11)) {
        var.update $dias_mes { value = 30 }
      }
      elseif ($mes == 2) {
        var.update $dias_mes { value = 28 }
        conditional {
          if (($ano|modulus:400) == 0 || (($ano|modulus:4) == 0 && ($ano|modulus:100) != 0)) {
            var.update $dias_mes { value = 29 }
          }
        }
      }
    }
    var $hoje { value = now|format_timestamp:"Ymd":"America/Sao_Paulo"|to_int }
    var $nascimento_ordenado { value = ($ano * 10000) + ($mes * 100) + $dia }
    conditional {
      if (($data_nascimento|strlen) != 10 || $ano < 1 || $mes < 1 || $mes > 12 || $dia < 1 || $dia > $dias_mes || $nascimento_ordenado > $hoje) {
        util.set_header { value = "HTTP/1.1 400 Bad Request" }
        return { value = {codigo: "DADOS_INVALIDOS", mensagem: "Confira os dados informados."} }
      }
    }
    // Dados exclusivamente fictícios no projeto acadêmico; persiste só o hash do payload.
    var $payload { value = {nome: $nome, data_nascimento: $data_nascimento, telefone: $telefone, cpf: $cpf, email: $email, celular: $celular}|json_encode }
    var $impressao { value = $payload|sha256 }
    db.query cadastro_paciente_operacao {
      where = $db.cadastro_paciente_operacao.conta_acesso_id == $auth.id && $db.cadastro_paciente_operacao.operacao_id == $bruto.operacao_id
      return = {type: "single"}
      output = ["id", "conta_acesso_id", "impressao_hmac", "paciente_id"]
    } as $operacao_existente
    conditional {
      if ($operacao_existente == null) {
        try_catch {
          try {
            db.transaction {
              stack {
                db.add paciente {
                  data = {nome: $nome, data_nascimento: $data_nascimento, telefone: $telefone, cpf: $cpf, email: $email, celular: $celular, situacao: "ativo", criado_em: now, atualizado_em: now}
                } as $novo_paciente
                db.add prontuario_paciente {
                  data = {paciente_id: $novo_paciente.id, aberto_em: now, situacao: "ativo"}
                } as $novo_prontuario
                db.add cadastro_paciente_operacao {
                  data = {conta_acesso_id: $auth.id, operacao_id: $bruto.operacao_id, impressao_hmac: $impressao, paciente_id: $novo_paciente.id}
                } as $comprovante
              }
            }
          }
          catch {
            // O rollback termina antes da reconsulta; nunca retornar o erro bruto.
            var $falha_gravacao { value = true }
          }
        }
      }
    }
    // Tanto sucesso quanto disputa concorrente usam somente comprovante confirmado.
    db.query cadastro_paciente_operacao {
      where = $db.cadastro_paciente_operacao.conta_acesso_id == $auth.id && $db.cadastro_paciente_operacao.operacao_id == $bruto.operacao_id
      return = {type: "single"}
      output = ["impressao_hmac", "paciente_id"]
    } as $confirmada
    conditional {
      if ($confirmada == null) {
        db.get paciente {
          field_name = "cpf"
          field_value = $cpf
          output = ["id"]
        } as $cpf_existente
        conditional {
          if ($cpf_existente != null) {
            util.set_header { value = "HTTP/1.1 409 Conflict" }
            return { value = {codigo: "CPF_DUPLICADO", mensagem: "CPF já cadastrado."} }
          }
        }
        util.set_header { value = "HTTP/1.1 503 Service Unavailable" }
        return { value = {codigo: "SERVICO_INDISPONIVEL", mensagem: "Não foi possível confirmar o cadastro."} }
      }
      elseif ($confirmada.impressao_hmac != $impressao) {
        util.set_header { value = "HTTP/1.1 409 Conflict" }
        return { value = {codigo: "OPERACAO_CONFLITANTE", mensagem: "Esta operação já foi usada com outros dados."} }
      }
    }
    db.get paciente {
      field_name = "id"
      field_value = $confirmada.paciente_id
      output = ["id", "nome", "situacao"]
    } as $paciente_confirmado
    conditional {
      if ($paciente_confirmado == null) {
        util.set_header { value = "HTTP/1.1 503 Service Unavailable" }
        return { value = {codigo: "SERVICO_INDISPONIVEL", mensagem: "Não foi possível confirmar o cadastro."} }
      }
    }
    util.set_header { value = "HTTP/1.1 201 Created" }
  }
  response = {paciente: {id: $paciente_confirmado.id, nome: $paciente_confirmado.nome, situacao: $paciente_confirmado.situacao}, operacao_id: $bruto.operacao_id}
  history = false
}
