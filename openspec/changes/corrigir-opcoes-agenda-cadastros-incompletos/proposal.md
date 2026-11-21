## Why

O usuário relatou falha em Home e Agendamento com Administrador e Recepcionista. A investigação encontrou Profissional ativo sem nome/CRO e com especialidade inválida retornado em GET `/agenda/opcoes`, invalidando a resposta usada nessas telas.

## What Changes

- Excluir cadastros sem nome das opções funcionais de agendamento no Xano, sem alterar registros históricos.
- Exigir nome e CRO preenchidos e vínculo de especialidade positivo nas opções de Profissional.
- Verificar Home e Nova Consulta nos dois perfis com REST real, além das regressões locais, investigando outras falhas que aparecerem nesse fluxo.
- Preservar formatos REST, autorização administrativa e regras de reservas.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `agenda-consultas`: opções de agendamento utilizáveis mesmo com cadastros legados incompletos.

## Impact

GET `/agenda/opcoes`, testes do contrato Python/JavaScript e regressões de Home e Nova Consulta. Sem exclusão, inativação ou edição de cadastros.
