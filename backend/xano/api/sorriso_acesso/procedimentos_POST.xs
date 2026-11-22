// Cria um Procedimento para uso no catÃ¡logo e nas Consultas.
query "procedimentos" verb=POST {
  api_group = "Sorriso Acesso"
  auth = "conta_acesso"
  input { }
  stack {
    util.set_header { value = "Cache-Control: no-store" duplicates = "replace" }
    function.run sorriso_validar_sessao { input = {conta_id: $auth.id, sessao_id: $auth.extras.sessao_id} } as $sessao
    db.get conta_acesso {
      field_name = "id"
      field_value = $auth.id
      output = ["id", "perfis", "situacao"]
    } as $solicitante
    conditional {
      if ($solicitante == null || $solicitante.situacao != "ativo" || ($solicitante.perfis|intersect:["administrador", "recepcionista", "profissional"]|count) == 0) {
        util.set_header { value = "HTTP/1.1 403 Forbidden" }
        return { value = {codigo: "ACESSO_NEGADO", mensagem: "Conta sem permissÃ£o para criar Procedimentos."} }
      }
    }
    try_catch {
      try { util.get_raw_input { encoding = "json" } as $bruto }
      catch {
        util.set_header { value = "HTTP/1.1 400 Bad Request" }
        return { value = {codigo: "DADOS_INVALIDOS", mensagem: "Informe o nome do Procedimento."} }
      }
    }
    conditional {
      if (($bruto|is_object) == false || ($bruto|get:"nome"|is_text) == false || (($bruto.nome|trim)|strlen) < 2 || (($bruto.nome|trim)|strlen) > 120) {
        util.set_header { value = "HTTP/1.1 400 Bad Request" }
        return { value = {codigo: "DADOS_INVALIDOS", mensagem: "Informe um nome de Procedimento entre 2 e 120 caracteres."} }
      }
    }
    var $nome { value = $bruto.nome|trim }
    db.query procedimento {
      where = $db.procedimento.nome == $nome
      return = {type: "single"}
      output = ["id", "nome", "ativo"]
    } as $existente
    conditional {
      if ($existente != null && $existente.ativo == true) {
        util.set_header { value = "HTTP/1.1 409 Conflict" }
        return { value = {codigo: "DUPLICIDADE", mensagem: "Já existe um Procedimento ativo com esse nome."} }
      }
    }
    db.add procedimento {
      data = {nome: $nome, ativo: true}
    } as $criado
    util.set_header { value = "HTTP/1.1 201 Created" }
  }
  response = {procedimento: {id: $criado.id, nome: $criado.nome, ativo: $criado.ativo}}
  history = false
  guid = "dZMoRcLqx6WaSGtZsh0JzS_YpUM"
}
