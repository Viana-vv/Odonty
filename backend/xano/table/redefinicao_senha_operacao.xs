// Schema LOCAL de referência, não aplicado/publicado. Sem rotas de escrita.
// Unicidade não comprova coordenação atômica: ativação depende de prova remota.
// Token bruto, senha, link, e-mail e payload do provedor nunca são persistidos.
table redefinicao_senha_operacao {
  auth = false
  schema {
    uuid id
    int solicitante_id { table = "conta_acesso" }
    int conta_acesso_id { table = "conta_acesso" }
    text email_hash
    int versao_credencial
    int geracao
    text? token_hash?
    timestamp criada_em
    timestamp consultavel_ate
    timestamp expira_em
    timestamp? envio_iniciado_em?
    timestamp envio_limite_em
    enum resultado_envio?="processando" {
      values = ["processando", "aceito", "falhou", "desconhecido"]
    }
    enum? terminal_link? {
      values = ["consumido", "substituido", "invalidado"]
    }
    timestamp? terminal_em?
  }
  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree|unique", field: [{name: "token_hash", op: "asc"}]}
    {type: "btree", field: [{name: "conta_acesso_id", op: "asc"}, {name: "criada_em", op: "asc"}]}
    {type: "btree", field: [{name: "solicitante_id", op: "asc"}, {name: "criada_em", op: "asc"}]}
  ]
}
