// Listagem administrativa independente das opções da Agenda.
query "pacientes" verb=GET {
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
        util.set_header { value = "HTTP/1.1 403 Forbidden" }
        return { value = {codigo: "ACESSO_NEGADO", mensagem: "Listagem de Pacientes disponível somente à equipe administrativa."} }
      }
    }
    db.query paciente {
      where = $db.paciente.situacao == "ativo"
      sort = {paciente.nome: "asc", paciente.id: "asc"}
      return = {type: "list"}
      output = ["id", "nome"]
    } as $pacientes
  }
  response = {pacientes: $pacientes}
  history = false
  guid = "9ajH66iSMJieOOCtcEw1B9Ac9r0"
}
