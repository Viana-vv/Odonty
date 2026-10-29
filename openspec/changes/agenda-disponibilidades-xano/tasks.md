## 1. Preparar publicação

- [ ] 1.1 Confirmar acesso seguro à Metadata API e identificar o workspace alvo sem registrar valores secretos; verificar a configuração de publicação. **Atualização de 29/10/2026:** `XANO_METADATA_TOKEN` e `XANO_WORKSPACE_ID` estão presentes no ambiente, assim como as URLs de API e Metadata. A presença das variáveis não comprova validade, acesso ao workspace ou rotas publicadas; nenhuma chamada administrativa foi executada nesta finalização de interface.
- [ ] 1.2 Comparar as quatro fontes Xano da proposta com as rotas existentes no workspace e registrar divergências antes de publicar. **Bloqueada por 1.1:** sem acesso ao workspace, não foi possível consultar as rotas publicadas.

## 2. Publicar e verificar

- [ ] 2.1 Publicar somente as rotas aprovadas no grupo `Sorriso Acesso` e confirmar sucesso pela Metadata API. **Bloqueada por 1.1 e 1.2:** nenhuma alteração foi enviada ao Xano.
- [x] 2.2 Executar testes unitários Python e JavaScript dos contratos GET, POST e PATCH sem requisições de rede; registrar os resultados (22 testes Python e 5 testes JavaScript aprovados nesta execução).
- [x] 2.3 Executar AppTests dos fluxos de Disponibilidade da Agenda; confirmar sucesso, erro e conflito (3 aprovados, 22 demais cenários da interface não selecionados nesta execução).
- [ ] 2.4 Validar, com Conta de Acesso e dados fictícios, os contratos no Xano publicado, autorizações e conflitos; respeitar limite de chamadas e preservar histórico. **Bloqueada por 2.1:** verificação real não executada.
- [x] 2.5 Validar a change com `openspec validate agenda-disponibilidades-xano --strict` (change válida nesta execução).
- [ ] 2.6 Após publicação e validação real, registrar evidências sem credenciais/dados pessoais.

## 3. Finalizar navegação de Nova Consulta

- [x] 3.1 Reproduzir com AppTests a data inicial incorreta e o cancelamento que não renderizava a Agenda imediatamente: dois testes falharam antes da correção.
- [x] 3.2 Inicializar Nova Consulta com a data selecionada na Agenda, incluindo seleção direta e navegação diária, sem modificar o filtro ao editar a data do formulário; usar o fuso da clínica quando não houver seleção anterior.
- [x] 3.3 Fazer Cancelar retornar imediatamente à Agenda sem enviar agendamento.
- [x] 3.4 Verificar regressão local de Agenda, Nova Consulta, transições e contratos: 87 testes Python aprovados na primeira rodada; após cobrir também a seleção direta da data, os 20 AppTests de Nova Consulta passaram. Os oito testes JavaScript das rotas envolvidas passaram sem rede. `openspec validate agenda-disponibilidades-xano --strict` passou e `git diff --check` não encontrou erros de whitespace.

### Limites da verificação de 29/10/2026

As verificações desta finalização são locais, com dados fictícios e rede simulada. Foram executadas zero requisições reais ao Xano. Não foi validada uma Conta de Acesso fictícia para executar os fluxos autenticados, nem foi confirmado o estado das rotas publicadas. As tarefas de publicação e validação real continuam pendentes; os ajustes locais não permitem declarar a integração aprovada nem arquivar a change. Não há comando específico de lint/build configurado no repositório; os módulos alterados foram importados pelos AppTests. A aparência em navegador e dispositivos não foi inspecionada nesta execução.
