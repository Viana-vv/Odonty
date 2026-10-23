## Purpose

Apresenta ao Administrador um resumo administrativo do dia, com informações obtidas pelos contratos já disponíveis e estados claros para ausência ou falha dos dados.

## ADDED Requirements

### Requirement: Resumo diário da Administração
A Visão geral do Administrador MUST mostrar o total de Consultas do dia, Consultas realizadas, Pacientes ativos e a próxima Consulta ativa. MUST listar até cinco Consultas ordenadas pelo horário, exibindo somente horário, nome do Paciente, nome do Profissional e situação. MUST NOT exibir dados de contato, motivo administrativo ou informações clínicas.

#### Scenario: Administrador abre a Visão geral com dados disponíveis
- **WHEN** o Administrador autenticado abre a Visão geral e os contratos existentes retornam dados
- **THEN** a interface apresenta as métricas calculadas, a próxima Consulta ativa e até cinco Consultas em ordem de horário

#### Scenario: Não há Consultas hoje
- **WHEN** a lista autorizada de Consultas do dia está vazia
- **THEN** as métricas de Consulta mostram zero, a próxima Consulta informa que nenhuma está marcada e a interface apresenta o estado vazio mantendo os atalhos disponíveis

#### Scenario: Falha ao carregar os dados
- **WHEN** um contrato necessário para o resumo falha
- **THEN** a interface apresenta uma mensagem compreensível, oferece nova tentativa e não apresenta informações parciais como resumo atualizado

#### Scenario: Sessão expirada ou sem permissão
- **WHEN** a API informa sessão expirada ou acesso não autorizado
- **THEN** a interface limpa os dados do resumo, informa a necessidade de novo acesso ou a falta de permissão e não mostra dados anteriores

#### Scenario: Conta de Acesso de outro perfil abre a Visão geral
- **WHEN** uma Conta de Acesso sem perfil Administrador abre a Visão geral
- **THEN** o painel administrativo não faz as leituras adicionais usadas por esse resumo e mantém o painel correspondente ao perfil existente
