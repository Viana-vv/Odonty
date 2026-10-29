// Lista Contas de Acesso com projection mínima; não retorna credenciais.
query "contas-acesso" verb=GET {
  api_group = "Sorriso Acesso"
  auth = "conta_acesso"
  input { }
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
    db.query conta_acesso {
      sort = {conta_acesso.nome: "asc", conta_acesso.id: "asc"}
      return = {type: "list"}
      output = ["id", "nome", "email", "perfis", "situacao"]
    } as $contas_acesso
    var $resultado { value = [] }
    foreach ($contas_acesso) {
      each as $conta {
        var $conta_formatada {
          value = {
            id       : $conta.id
            nome     : $conta.nome
            email    : $conta.email
            perfis   : $conta.perfis
            situacao : $conta.situacao
          }
        }
        var.update $resultado {
          value = $resultado|push:$conta_formatada
        }
      }
    }
  }
  response = {contas_acesso: $resultado}
  history = false
  guid = "92f33335a87b4985856551d2610dfb84"
}
