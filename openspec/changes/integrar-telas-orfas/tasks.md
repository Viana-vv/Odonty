## 1. Navegação e acesso por perfil

- [ ] 1.1 Registrar as rotas distintas de Exames e Reagendamento, módulos e perfis permitidos; verificar regras de visibilidade e acesso por testes unitários de navegação.
- [ ] 1.2 Integrar menu e despacho dessas rotas às interfaces existentes; verificar abertura com cliente/Conta de Acesso atuais e ausência de chamadas para perfis não autorizados nos testes de interface.
- [ ] 1.3 Cobrir módulo ausente, renderer inválido e rota direta não permitida; verificar fallback para uma área válida e mensagem segura nos testes.

## 2. Procedimentos da Consulta com contexto

- [ ] 2.1 Adicionar ação contextual na Consulta do Profissional sem alterar o catálogo administrativo; verificar distinção das rotas e perfis nos testes.
- [ ] 2.2 Passar a Consulta selecionada ao renderer existente e limpar/substituir contexto ao trocar de Consulta, sair da área ou perder perfil; verificar o identificador entregue e a limpeza de estado em testes.
- [ ] 2.3 Cobrir acesso direto sem contexto e contexto inválido; verificar que não há chamadas ao cliente de Procedimentos e que a interface oferece retorno à Agenda.

## 3. Verificação integrada

- [ ] 3.1 Executar os testes focados de navegação, roteamento e telas afetadas; verificar perfis permitidos/negados, contexto correto, fallback e regressões do catálogo.
- [ ] 3.2 Executar `openspec validate integrar-telas-orfas --strict` e `git diff --check`; verificar validação estrita sem erros e diff sem problemas de whitespace.
