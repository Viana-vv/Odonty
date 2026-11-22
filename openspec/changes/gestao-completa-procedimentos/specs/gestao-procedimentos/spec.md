## Purpose

Permitir que a equipe administrativa mantenha um catálogo confiável de Procedimentos sem apagar dados históricos usados em Consultas e atendimentos.

## ADDED Requirements

### Requirement: Cadastro e manutenção do Procedimento

O sistema SHALL permitir que Administrador, Recepcionista e Profissional criem Procedimentos. O sistema SHALL permitir que Administrador e Recepcionista editem e inativem Procedimentos. Todas as autorizações SHALL ser validadas no Xano.

#### Scenario: Administrador, Recepcionista ou Profissional cadastra Procedimento válido

- **WHEN** Administrador, Recepcionista ou Profissional informa um nome válido e salva o cadastro
- **THEN** o Procedimento ativo é persistido e aparece no catálogo

#### Scenario: Impedir cadastro inválido ou duplicado

- **WHEN** o usuário envia nome vazio, inválido ou já utilizado por outro Procedimento ativo
- **THEN** o sistema rejeita a operação e informa um erro compreensível

#### Scenario: Editar Procedimento

- **WHEN** Administrador ou Recepcionista altera os dados permitidos de um Procedimento
- **THEN** o catálogo exibe os dados atualizados sem alterar vínculos históricos

#### Scenario: Inativar Procedimento

- **WHEN** Administrador ou Recepcionista inativa um Procedimento
- **THEN** ele deixa de aparecer como opção para novas Consultas, mas permanece visível no histórico das Consultas existentes

#### Scenario: Profissional não edita o catálogo

- **WHEN** Profissional tenta editar ou inativar um Procedimento
- **THEN** o Xano rejeita a operação e nenhum dado é alterado

#### Scenario: Paciente não gerencia Procedimentos

- **WHEN** Paciente tenta criar, editar ou inativar um Procedimento
- **THEN** o Xano rejeita a operação e nenhum dado é alterado

### Requirement: Catálogo por situação

O sistema SHALL exibir a situação do Procedimento e SHALL permitir filtrar ativos e inativos para Administrador e Recepcionista.

#### Scenario: Filtrar catálogo

- **WHEN** o usuário seleciona uma situação ou pesquisa por nome
- **THEN** o sistema exibe somente os Procedimentos correspondentes
