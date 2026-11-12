// Agregado autorizado de um Prontuário por Paciente.
// Conteúdo clínico não é retornado para Administrador ou Recepcionista.
query "prontuarios/{id}" verb=GET {
  api_group = "Sorriso Acesso"
  auth = "conta_acesso"
  input {
    int id
  }
  stack {
    util.set_header {
      value = "Cache-Control: no-store"
      duplicates = "replace"
    }
    function.run sorriso_validar_sessao {
      input = {conta_id: $auth.id, sessao_id: $auth.extras.sessao_id}
    } as $sessao
    db.get conta_acesso {
      field_name = "id"
      field_value = $auth.id
      output = ["id", "perfis", "situacao"]
    } as $solicitante
    conditional {
      if ($solicitante == null || $solicitante.situacao != "ativo") {
        util.set_header { value = "HTTP/1.1 403 Forbidden" }
        return { value = {codigo: "ACESSO_NEGADO", mensagem: "Conta sem permissão para consultar o Prontuário."} }
      }
      elseif ($input.id <= 0) {
        util.set_header { value = "HTTP/1.1 400 Bad Request" }
        return { value = {codigo: "DADOS_INVALIDOS", mensagem: "Identificador de Paciente inválido."} }
      }
      elseif (($solicitante.perfis|intersect:["administrador", "recepcionista"]|count) > 0) {
        util.set_header { value = "HTTP/1.1 403 Forbidden" }
        return { value = {codigo: "ACESSO_NEGADO", mensagem: "Perfis administrativos não podem consultar conteúdo clínico."} }
      }
      elseif (($solicitante.perfis|intersect:["paciente", "profissional"]|count) == 0) {
        util.set_header { value = "HTTP/1.1 403 Forbidden" }
        return { value = {codigo: "ACESSO_NEGADO", mensagem: "Conta sem permissão para consultar o Prontuário."} }
      }
    }

    db.get paciente {
      field_name = "id"
      field_value = $input.id
      output = ["id", "nome", "cpf", "data_nascimento", "telefone", "celular", "email", "situacao"]
    } as $paciente
    conditional {
      if ($paciente == null || $paciente.situacao == "inativo") {
        util.set_header { value = "HTTP/1.1 404 Not Found" }
        return { value = {codigo: "RECURSO_NAO_ENCONTRADO", mensagem: "Prontuário não encontrado no escopo permitido."} }
      }
    }

    var $profissional_escopo { value = null }
    conditional {
      if (($solicitante.perfis|intersect:["paciente"]|count) > 0) {
        db.get paciente {
          field_name = "conta_acesso_id"
          field_value = $auth.id
          output = ["id", "situacao"]
        } as $paciente_autenticado
        conditional {
          if ($paciente_autenticado == null || $paciente_autenticado.id != $paciente.id || $paciente_autenticado.situacao != "ativo") {
            util.set_header { value = "HTTP/1.1 404 Not Found" }
            return { value = {codigo: "RECURSO_NAO_ENCONTRADO", mensagem: "Prontuário não encontrado no escopo permitido."} }
          }
        }
      }
      else {
        db.get profissional {
          field_name = "conta_acesso_id"
          field_value = $auth.id
          output = ["id", "situacao"]
        } as $profissional_autenticado
        conditional {
          if ($profissional_autenticado == null || $profissional_autenticado.situacao != "Ativo") {
            util.set_header { value = "HTTP/1.1 403 Forbidden" }
            return { value = {codigo: "ACESSO_NEGADO", mensagem: "Profissional sem acesso clínico ativo."} }
          }
        }
        db.query consulta {
          where = $db.consulta.paciente_id == $paciente.id && $db.consulta.profissional_id == $profissional_autenticado.id
          return = {type: "list"}
          output = ["id"]
        } as $consultas_autorizadas
        conditional {
          if (($consultas_autorizadas|count) == 0) {
            util.set_header { value = "HTTP/1.1 404 Not Found" }
            return { value = {codigo: "RECURSO_NAO_ENCONTRADO", mensagem: "Prontuário não encontrado no escopo permitido."} }
          }
        }
        var.update $profissional_escopo { value = $profissional_autenticado.id }
      }
    }

    db.get prontuario_paciente {
      field_name = "paciente_id"
      field_value = $paciente.id
      output = ["id", "paciente_id", "aberto_em", "situacao"]
    } as $prontuario
    conditional {
      if ($prontuario == null || $prontuario.situacao != "ativo") {
        util.set_header { value = "HTTP/1.1 404 Not Found" }
        return { value = {codigo: "RECURSO_NAO_ENCONTRADO", mensagem: "Prontuário não encontrado no escopo permitido."} }
      }
    }

    var $anamnese { value = [] }
    var $historico_odontologico { value = [] }
    var $odontograma { value = [] }
    var $exame_clinico { value = [] }
    var $diagnosticos { value = [] }
    var $plano_tratamento { value = [] }
    var $prescricoes { value = [] }
    var $documentos { value = [] }
    var $secoes_query { value = [] }
    conditional {
      if ($profissional_escopo != null) {
        db.query prontuario_secao {
          where = $db.prontuario_secao.paciente_id == $paciente.id && $db.prontuario_secao.profissional_id == $profissional_escopo
          sort = {prontuario_secao.criado_em: "desc", prontuario_secao.id: "desc"}
          return = {type: "list"}
          output = ["id", "prontuario_id", "paciente_id", "consulta_id", "profissional_id", "tipo", "conteudo", "liberado_paciente", "versao", "criado_em"]
        } as $secoes_query
      }
      else {
        db.query prontuario_secao {
          where = $db.prontuario_secao.paciente_id == $paciente.id && $db.prontuario_secao.liberado_paciente == true
          sort = {prontuario_secao.criado_em: "desc", prontuario_secao.id: "desc"}
          return = {type: "list"}
          output = ["id", "prontuario_id", "paciente_id", "consulta_id", "tipo", "conteudo", "versao", "criado_em"]
        } as $secoes_query
      }
    }
    foreach ($secoes_query) {
      each as $secao {
        var $secao_formatada { value = {id: $secao.id, prontuario_id: $secao.prontuario_id, paciente_id: $secao.paciente_id, consulta_id: $secao.consulta_id, profissional_id: $secao.profissional_id, tipo: $secao.tipo, conteudo: $secao.conteudo, liberado_paciente: $secao.liberado_paciente, versao: $secao.versao, criado_em: $secao.criado_em} }
        conditional {
          if ($secao.tipo == "Anamnese") {
            var.update $anamnese { value = $anamnese|push:$secao_formatada }
          }
          elseif ($secao.tipo == "Histórico Odontológico") {
            var.update $historico_odontologico { value = $historico_odontologico|push:$secao_formatada }
          }
          elseif ($secao.tipo == "Odontograma") {
            var.update $odontograma { value = $odontograma|push:$secao_formatada }
          }
          elseif ($secao.tipo == "Exame Clínico") {
            var.update $exame_clinico { value = $exame_clinico|push:$secao_formatada }
          }
          elseif ($secao.tipo == "Diagnóstico") {
            var.update $diagnosticos { value = $diagnosticos|push:$secao_formatada }
          }
          elseif ($secao.tipo == "Plano de Tratamento") {
            var.update $plano_tratamento { value = $plano_tratamento|push:$secao_formatada }
          }
          elseif ($secao.tipo == "Prescrição") {
            var.update $prescricoes { value = $prescricoes|push:$secao_formatada }
          }
          elseif ($secao.tipo == "Documento") {
            var.update $documentos { value = $documentos|push:$secao_formatada }
          }
        }
      }
    }

    var $procedimentos { value = [] }
    db.query consulta_procedimento {
      return = {type: "list"}
      output = ["id", "consulta_id", "procedimento_id", "profissional_id", "situacao", "realizado_por_profissional_id", "realizado_em", "criado_em"]
    } as $procedimentos_vinculos
    foreach ($procedimentos_vinculos) {
      each as $vinculo {
        db.get consulta {
          field_name = "id"
          field_value = $vinculo.consulta_id
          output = ["id", "paciente_id", "profissional_id"]
        } as $consulta_procedimento
        conditional {
          if ($consulta_procedimento != null && $consulta_procedimento.paciente_id == $paciente.id && ($profissional_escopo == null || $consulta_procedimento.profissional_id == $profissional_escopo)) {
            db.get procedimento {
              field_name = "id"
              field_value = $vinculo.procedimento_id
              output = ["id", "nome"]
            } as $procedimento
            var $procedimento_nome { value = null }
            conditional {
              if ($procedimento != null) {
                var.update $procedimento_nome { value = $procedimento.nome }
              }
            }
            var.update $procedimentos { value = $procedimentos|push:{id: $vinculo.id, consulta_id: $vinculo.consulta_id, procedimento_id: $vinculo.procedimento_id, procedimento_nome: $procedimento_nome, profissional_id: $vinculo.profissional_id, situacao: $vinculo.situacao, realizado_por_profissional_id: $vinculo.realizado_por_profissional_id, realizado_em: $vinculo.realizado_em, criado_em: $vinculo.criado_em} }
          }
        }
      }
    }

    var $exames { value = [] }
    db.query exame {
      where = $db.exame.paciente_id == $paciente.id
      sort = {exame.solicitado_em: "desc", exame.id: "desc"}
      return = {type: "list"}
      output = ["id", "paciente_id", "consulta_id", "profissional_id", "tipo", "situacao", "solicitado_em", "realizado_em", "resultado", "observacoes"]
    } as $exames_query
    foreach ($exames_query) {
      each as $exame {
        conditional {
          if ($profissional_escopo == null || $exame.profissional_id == $profissional_escopo) {
            var $resultado_exame { value = null }
            conditional {
              if ($profissional_escopo != null || $exame.situacao == "Resultado disponível") {
                var.update $resultado_exame { value = $exame.resultado }
              }
            }
            var.update $exames { value = $exames|push:{id: $exame.id, paciente_id: $exame.paciente_id, consulta_id: $exame.consulta_id, profissional_id: $exame.profissional_id, tipo: $exame.tipo, situacao: $exame.situacao, solicitado_em: $exame.solicitado_em, realizado_em: $exame.realizado_em, resultado: $resultado_exame, observacoes: $exame.observacoes} }
          }
        }
      }
    }

    var $evolucoes { value = [] }
    db.query registro_clinico {
      where = $db.registro_clinico.paciente_id == $paciente.id
      sort = {registro_clinico.registrado_em: "desc", registro_clinico.id: "desc"}
      return = {type: "list"}
      output = ["id", "prontuario_id", "paciente_id", "profissional_id", "consulta_id", "conteudo", "liberado_paciente", "concluido", "registrado_em"]
    } as $registros_query
    foreach ($registros_query) {
      each as $registro {
        conditional {
          if (($profissional_escopo != null && $registro.profissional_id == $profissional_escopo) || ($profissional_escopo == null && $registro.liberado_paciente == true)) {
            var.update $evolucoes { value = $evolucoes|push:{id: $registro.id, prontuario_id: $registro.prontuario_id, paciente_id: $registro.paciente_id, profissional_id: $registro.profissional_id, consulta_id: $registro.consulta_id, conteudo: $registro.conteudo, liberado_paciente: $registro.liberado_paciente, concluido: $registro.concluido, registrado_em: $registro.registrado_em} }
          }
        }
      }
    }
  }
  response = {paciente: {id: $paciente.id, nome: $paciente.nome, cpf: $paciente.cpf, data_nascimento: $paciente.data_nascimento, telefone: $paciente.telefone, celular: $paciente.celular, email: $paciente.email, endereco: null}, prontuario: $prontuario, anamnese: $anamnese, historico_odontologico: $historico_odontologico, odontograma: $odontograma, exame_clinico: $exame_clinico, diagnosticos: $diagnosticos, plano_tratamento: $plano_tratamento, procedimentos: $procedimentos, exames: $exames, prescricoes: $prescricoes, evolucoes: $evolucoes, documentos: $documentos}
  history = false
}
