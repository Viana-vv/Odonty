## Why

O catálogo de Procedimentos ainda depende de GET `/agenda/opcoes`. Um Profissional incompleto faz a validação das opções falhar e impede consultar Procedimentos válidos.

## What Changes

- Criar GET `/procedimentos` com sessão válida e autorização de Administrador e Recepcionista, retornando somente identificador e nome dos Procedimentos ativos.
- Usar a rota exclusiva na tela com cache próprio, busca e atualização manual.
- Liberar consulta do catálogo para Recepcionista, conforme esclarecimento do usuário, no menu, na tela e no Xano. Cadastro de Procedimentos e mudanças nas opções da Agenda ficam fora deste escopo.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `catalogo-procedimentos`: permitir consulta por Recepcionista e consultar somente Procedimentos sem depender de Pacientes ou Profissionais.

## Impact

Nova rota Xano, cliente REST, tela e contratos Python/JavaScript sem rede. Sem alteração de tabelas ou dados. Ajustes locais na `main`, conforme orientação vigente do usuário.
