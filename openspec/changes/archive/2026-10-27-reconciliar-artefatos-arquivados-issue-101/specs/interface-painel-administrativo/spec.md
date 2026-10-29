# interface painel administrativo Specification

## Purpose

Restaurar na especificação vigente os requisitos aprovados nos deltas arquivados para a capacidade `interface-painel-administrativo`.

## ADDED Requirements

### Requirement: Limite de chamadas do resumo
O resumo administrativo MUST reutilizar as respostas completas e bem-sucedidas para a mesma Conta de Acesso e data local por até vinte segundos. MUST descartar o cache ao expirar a janela, trocar de Conta de Acesso, encerrar a sessão ou falhar uma leitura. MUST NOT exibir respostas parciais nem reutilizar dados de outra sessão.

#### Scenario: O Administrador atualiza o painel dentro da janela de cache
- **WHEN** a mesma Conta de Acesso provoca um novo render do painel dentro de vinte segundos
- **THEN** a interface reutiliza o resumo em memória e não envia novamente as duas leituras ao Xano

#### Scenario: O cache expira ou a sessão termina
- **WHEN** passam vinte segundos ou a Conta de Acesso encerra a sessão
- **THEN** a resposta antiga deixa de ser reutilizável e uma próxima leitura autorizada consulta o Xano novamente

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

