// Revoga somente a sessão atual, inclusive após perda de permissão.
query "auth/logout" verb=POST {
  api_group = "Sorriso Acesso"
  auth = "conta_acesso"
  input { }
  stack {
    util.set_header { value = "Cache-Control: no-store" }
    function.run sorriso_validar_sessao {
      input = {conta_id: $auth.id, sessao_id: $auth.extras.sessao_id, encerrar: true}
    } as $sessao
    conditional {
      if ($sessao.revogada_em == null) {
        db.edit sessao_acesso {
          field_name = "id"
          field_value = $sessao.id
          data = {revogada_em: now}
        } as $revogada
      }
    }
    util.set_header { value = "HTTP/1.1 204 No Content" }
  }
  response = null
  history = false
  guid = "4sDO0GCKzEJCV7GmO4j3D9e4BHs"
}

