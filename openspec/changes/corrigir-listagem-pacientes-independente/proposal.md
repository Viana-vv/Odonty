## Why

A tela Pacientes depende de GET `/agenda/opcoes`, portanto um Profissional ativo sem nome impede a exibição de todos os Pacientes e gera uma mensagem enganosa de conexão. A investigação reproduziu a falha; o usuário autorizou separar o carregamento para corrigir o defeito da Issue #146.

## What Changes

- Criar GET `/pacientes` autenticado, exclusivo para Administrador e Recepcionista, retornando somente identificador e nome dos Pacientes ativos.
- Usar essa rota na tela Pacientes com cache privado por sessão e atualização após cadastro/edição.
- Verificar que falhas ou cadastros inválidos nas opções da Agenda não interferem nessa tela.
- Preservar cadastro, edição, busca, visual e opções de agendamento existentes. Correção de cadastros de Profissional e mudanças em outras telas ficam fora do escopo.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `interface-pacientes`: carregar a listagem administrativa independentemente das opções da Agenda, com autorização no Xano e dados mínimos.

## Impact

Nova rota Xano, cliente REST Python, tela Pacientes e testes de contrato Python/JavaScript e de interface. A rota deve ser publicada antes de disponibilizar o frontend atualizado. Nenhuma tabela ou registro cadastral será alterado.
