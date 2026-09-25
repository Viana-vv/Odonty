// Retorna somente a identificação da própria Conta de Acesso.
query "auth/me" verb=GET {
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
      output = ["id", "nome", "perfis", "situacao"]
    } as $conta
    conditional {
      if ($conta.situacao != "ativo" || ($conta.perfis|intersect:["administrador", "recepcionista", "profissional"]|count) == 0) {
        util.set_header { value = "HTTP/1.1 403 Forbidden" }
        return { value = {codigo: "ACESSO_NEGADO", mensagem: "Acesso não permitido."} }
      }
    }
  }
  response = {conta: $conta, expira_em: $sessao.expira_em|format_timestamp:"c":"UTC"}
  history = false
  guid = "g9yspk4_0qqyOQyfVNhF1oDQ0_g"
}

