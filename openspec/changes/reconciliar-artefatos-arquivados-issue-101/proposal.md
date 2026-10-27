## Why

A auditoria da Issue #101 encontrou uma retomada arquivada de cadastro de Profissional sem diretório `specs/`. A proposta da retomada afirma que não introduziu capabilities e que apenas corrigiu divergências locais; contudo, a change original `cadastro-profissional-admin` contém os requisitos que delimitam essa retomada. O OpenSpec CLI não oferece comando para restaurar ou alterar diretamente uma change arquivada.

## What Changes

- Registrar nesta change ativa a especificação de `cadastro-profissional` recuperada literalmente da change original arquivada, como fonte documental para a retomada sem acrescentar requisitos.
- Registrar em design a proveniência e a limitação do CLI: o registro fica nesta nova change, não reescreve retroativamente o diretório arquivado.
- Reconciliar as tarefas históricas somente quando há evidência explícita; manter abertas as verificações remotas pendentes e os requisitos processuais que não podem ser cumpridos retroativamente.

Fora do escopo: alterar código funcional, specs principais, integração Xano, criar Issues/PRs retroativos ou reescrever diretórios arquivados manualmente.

## Capabilities

### New Capabilities

Nenhuma. A spec incluída é reprodução documental de requisitos já aprovados, sem mudança de comportamento.

### Modified Capabilities

Nenhuma.

## Impact

Somente artefatos OpenSpec nesta change ativa e tarefas arquivadas com evidência verificável. Nenhum código ou serviço externo será alterado.
