## ADDED Requirements

### Requirement: Expor retificações no histórico autorizado
O Xano MUST retornar, junto a cada Registro Clínico autorizado, a lista cronológica de suas retificações, contendo conteúdo retificado, justificativa, Profissional autor e data. O Registro Clínico original MUST permanecer inalterado.

#### Scenario: Profissional consulta registro retificado
- **WHEN** Profissional autorizado consulta um Registro Clínico com retificações
- **THEN** recebe original e retificações ordenadas por data, sem perda de autoria ou justificativa

#### Scenario: Paciente consulta registro liberado retificado
- **WHEN** Paciente autenticado consulta o próprio Registro Clínico liberado
- **THEN** recebe original e retificações vinculadas ao mesmo registro, respeitando a liberação original

#### Scenario: Perfil administrativo consulta histórico
- **WHEN** Recepcionista ou Administrador tenta consultar histórico clínico
- **THEN** o Xano nega acesso e não revela a existência de registros ou retificações
