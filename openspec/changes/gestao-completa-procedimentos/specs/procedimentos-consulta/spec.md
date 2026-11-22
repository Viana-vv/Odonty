## Purpose

Permitir que o Profissional planeje, acompanhe e registre os Procedimentos de uma Consulta, mantendo o histórico do atendimento.

## ADDED Requirements

### Requirement: Vínculo de Procedimento com Consulta

O sistema SHALL permitir que um Profissional autorizado adicione um ou mais Procedimentos ativos à sua Consulta. Um vínculo SHALL possuir Consulta, Procedimento, situação e responsável quando realizado.

#### Scenario: Adicionar Procedimento durante o atendimento

- **WHEN** o Profissional abre uma Consulta autorizada e seleciona um Procedimento ativo
- **THEN** o sistema cria o vínculo como planejado e exibe o Procedimento na Consulta

#### Scenario: Recusar Procedimento inativo ou Consulta fora do escopo

- **WHEN** o Profissional tenta vincular Procedimento inativo ou Consulta que não pertence ao seu escopo
- **THEN** o Xano rejeita a operação e não cria vínculo

#### Scenario: Evitar vínculo duplicado ativo

- **WHEN** o Profissional tenta adicionar novamente o mesmo Procedimento à mesma Consulta enquanto já existe vínculo ativo
- **THEN** o sistema rejeita a duplicidade ou mantém somente um vínculo ativo

### Requirement: Situação do Procedimento da Consulta

O sistema SHALL permitir ao Profissional marcar um Procedimento planejado como realizado ou cancelado. A alteração SHALL preservar o histórico e registrar profissional e data quando realizado.

#### Scenario: Marcar como realizado

- **WHEN** o Profissional confirma a realização de um Procedimento planejado
- **THEN** o vínculo passa para realizado e registra responsável e data

#### Scenario: Cancelar Procedimento planejado

- **WHEN** o Profissional cancela um Procedimento planejado
- **THEN** o vínculo passa para cancelado e continua disponível no histórico

#### Scenario: Usuário não profissional

- **WHEN** Administrador, Recepcionista ou Paciente tenta alterar o vínculo clínico
- **THEN** o Xano rejeita a operação

### Requirement: Procedimentos selecionados no agendamento

O sistema SHALL permitir que Administrador e Recepcionista selecionem somente Procedimentos ativos ao criar uma Consulta. Procedimentos já vinculados SHALL aparecer no histórico mesmo após inativação no catálogo.

#### Scenario: Agendar com Procedimentos ativos

- **WHEN** a equipe administrativa agenda uma Consulta e seleciona Procedimentos ativos
- **THEN** a Consulta é criada com os vínculos planejados

#### Scenario: Tentar agendar com Procedimento inativo

- **WHEN** a requisição de agendamento contém Procedimento inativo
- **THEN** o Xano rejeita a requisição
