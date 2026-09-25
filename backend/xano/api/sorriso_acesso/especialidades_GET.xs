// Lista somente especialidades ativas para o cadastro administrativo.
query especialidades verb=GET {
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
    db.query especialidade {
      where = $db.especialidade.ativo == true
      sort = {especialidade.nome: "asc", especialidade.id: "asc"}
      return = {type: "list"}
      output = ["id", "nome"]
    } as $especialidades
  }
  response = {especialidades: $especialidades}
  history = false
  guid = "JBNNTA47bIaVc73Pc0TRiEuAGiM"
}
