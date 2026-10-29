## ADDED Requirements

### Requirement: Apresentar trilha de retificações sem apagar o original
A interface MUST exibir as retificações retornadas pelo Xano associadas ao Registro Clínico original, incluindo data e justificativa disponíveis, sem fabricar autoria ou substituir o conteúdo anterior.

#### Scenario: Histórico contém retificação
- **WHEN** o Xano retorna uma ou mais retificações do Registro Clínico
- **THEN** a interface apresenta original e versões retificadas na ordem recebida, com os metadados fornecidos

#### Scenario: Histórico sem retificações
- **WHEN** o Xano retorna lista vazia de retificações
- **THEN** a interface mantém a apresentação do Registro Clínico sem criar conteúdo de auditoria
