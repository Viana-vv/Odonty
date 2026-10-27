# interface painel recepcao Specification

## Purpose

Restaurar na especificação vigente os requisitos aprovados nos deltas arquivados para a capacidade `interface-painel-recepcao`.

## ADDED Requirements

### Requirement: Resumo diário da Recepção
A Visão geral conectada apresentada à Recepção MUST carregar Consultas do dia autenticadas no escopo autorizado pelo Xano e mostrar totais de Consultas, Consultas realizadas, próxima Consulta ativa e Consultas confirmadas. MUST apresentar a agenda do dia ordenada por horário, limitada às cinco primeiras Consultas, exibindo somente horário, nome do Paciente, nome do Profissional e situação. MUST NOT exibir dados de contato, motivo administrativo, Procedimentos, Prontuário, Registro Clínico, Exame ou outras informações clínicas.

#### Scenario: Recepção abre o painel com Consultas
- **WHEN** uma Recepcionista autenticada abre a Visão geral e o Xano retorna Consultas do dia
- **THEN** o painel calcula os indicadores a partir da resposta, mostra até cinco Consultas em ordem de horário e apresenta a próxima Consulta que ainda não esteja realizada, cancelada ou marcada como falta

#### Scenario: Dia sem Consultas
- **WHEN** o Xano retorna uma lista vazia para o dia
- **THEN** o painel apresenta indicadores zerados, informa que não há Consultas para hoje e mantém os atalhos funcionais disponíveis

#### Scenario: Falha ao carregar Consultas
- **WHEN** a API falha ao carregar o resumo
- **THEN** o painel apresenta uma mensagem compreensível, oferece atualização manual e não apresenta dados de cache como atuais

#### Scenario: Sessão expirada ou acesso recusado
- **WHEN** o Xano responde que a sessão expirou ou que a Conta de Acesso não possui autorização
- **THEN** a interface limpa a sessão em caso de expiração, remove o resumo armazenado e não apresenta nomes ou Consultas em cache

#### Scenario: Conta de Acesso de outro perfil
- **WHEN** Administrador, Profissional ou Paciente abre a Visão geral conectada
- **THEN** a interface preserva o comportamento já existente para esses perfis e não executa a consulta adicional exclusiva do painel da Recepção

### Requirement: Atalhos operacionais do painel da Recepção
A Visão geral da Recepção MUST permitir abrir a Agenda conectada e MUST exibir somente atalhos de cadastro autorizados e já implementados. O painel MUST manter a autorização e o escopo das Consultas sob responsabilidade do Xano.

#### Scenario: Abrir Agenda pelo painel
- **WHEN** a Recepcionista seleciona o atalho para visualizar a Agenda
- **THEN** a aplicação navega para a Agenda conectada existente

#### Scenario: Abrir cadastro de Paciente
- **WHEN** o cadastro de Paciente está habilitado para a Recepcionista
- **THEN** o painel mantém o atalho funcional para o formulário existente de Paciente

