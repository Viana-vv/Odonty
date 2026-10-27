## 1. Preparar publicação

- [ ] 1.1 Confirmar acesso seguro à Metadata API e identificar o workspace alvo sem registrar valores secretos; verificar a configuração de publicação.
- [ ] 1.2 Comparar as quatro fontes Xano da proposta com as rotas existentes no workspace e registrar divergências antes de publicar.

## 2. Publicar e verificar

- [ ] 2.1 Publicar somente as rotas aprovadas no grupo `Sorriso Acesso` e confirmar sucesso pela Metadata API.
- [x] 2.2 Executar testes unitários Python e JavaScript dos contratos GET, POST e PATCH sem requisições de rede; registrar os resultados (25 testes Python e 6 testes JavaScript aprovados).
- [x] 2.3 Executar AppTests dos fluxos de Disponibilidade da Agenda; confirmar sucesso, erro e conflito (6 aprovados, 19 demais cenários da interface não selecionados).
- [ ] 2.4 Validar, com Conta de Acesso e dados fictícios, os contratos no Xano publicado, autorizações e conflitos; respeitar limite de chamadas e preservar histórico.
- [x] 2.5 Validar a change com `openspec validate agenda-disponibilidades-xano --strict` (change válida).
- [ ] 2.6 Após publicação e validação real, registrar evidências sem credenciais/dados pessoais.
