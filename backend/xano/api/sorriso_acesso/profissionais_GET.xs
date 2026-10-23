// Lista dados cadastrais administrativos sem expor Conta de Acesso ou documentos.
query profissionais verb=GET {
  api_group = "Sorriso Acesso"
  auth = "conta_acesso"
  input {
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
      if ($solicitante == null || $solicitante.situacao != "ativo" || ($solicitante.perfis|intersect:["administrador", "recepcionista"]|count) == 0) {
        util.set_header {
          value = "HTTP/1.1 403 Forbidden"
          duplicates = "replace"
        }
        return {
          value = {
            codigo  : "ACESSO_NEGADO"
            mensagem: "Acesso permitido somente à equipe administrativa."
          }
        }
      }
    }
    db.query profissional {
      sort = {profissional.nome: "asc", profissional.id: "asc"}
      return = {type: "list"}
      output = [
        "id"
        "nome"
        "cro"
        "email"
        "telefone"
        "situacao"
        "especialidade_id"
      ]
    } as $lista
    var $resultado { value = [] }
    foreach ($lista) {
      each as $item {
        db.get especialidade {
          field_name = "id"
          field_value = $item.especialidade_id
          output = ["id", "nome"]
        } as $especialidade
        var $profissional_formatado {
          value = {
            id           : $item.id
            nome         : $item.nome
            cro          : $item.cro
            especialidade: {id: $especialidade.id, nome: $especialidade.nome}
            email        : $item.email
            telefone     : $item.telefone
            situacao     : $item.situacao|to_lower
          }
        }
        var.update $resultado {
          value = $resultado|push:$profissional_formatado
        }
      }
    }
  }
  response = {profissionais: $resultado}
  history = false
  guid = "wicpdSickbi3uescydlCa9dy_YU"
}
