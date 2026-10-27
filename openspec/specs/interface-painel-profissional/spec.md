# interface-painel-profissional Specification

## Purpose
Restaurar na especificação vigente os requisitos aprovados nos deltas arquivados para a capacidade `interface-painel-profissional`.

## Requirements

### Requirement: Estados de acesso e falha do painel do Profissional
A Visão geral MUST apresentar mensagens seguras para falha de API, sessão expirada ou acesso recusado. Em caso de sessão expirada MUST limpar a Conta de Acesso da sessão local. MUST NOT exibir detalhes técnicos nem manter Consultas anteriores visíveis como atuais após erro.

#### Scenario: Sessão expirada
- **WHEN** `GET /consultas` retorna HTTP 401
- **THEN** a tela limpa a sessão local e informa que a sessão expirou

#### Scenario: Acesso recusado
- **WHEN** `GET /consultas` retorna HTTP 403
- **THEN** a tela informa que a Conta de Acesso não tem permissão e não mostra dados da resposta anterior

#### Scenario: Falha temporária da API
- **WHEN** a leitura retorna outro erro de API
- **THEN** a tela mostra uma mensagem compreensível e uma ação existente de nova tentativa sem expor mensagem técnica

### Requirement: Cache e atalhos do painel do Profissional
A tela MUST reutilizar a leitura diária em cache por até vinte segundos, vinculada à Conta de Acesso e à data local, e MUST continuar deixando autenticação, autorização e filtragem de Consultas sob responsabilidade do Xano. MUST manter os atalhos existentes para Agenda e Prontuários conforme a disponibilidade e autorização atuais, sem criar novas ações.

#### Scenario: Rerun dentro da validade do cache
- **WHEN** a Visão geral é renderizada novamente para a mesma Conta de Acesso e data em até vinte segundos
- **THEN** a tela reutiliza a resposta cacheada sem outra chamada ao Xano

#### Scenario: Troca de sessão ou expiração do cache
- **WHEN** a Conta de Acesso muda, a data muda ou o cache atinge vinte segundos
- **THEN** a resposta de outra sessão ou data não é reutilizada e uma leitura autorizada é feita antes da apresentação

#### Scenario: Navegação pelos atalhos existentes
- **WHEN** o Profissional seleciona Agenda ou Prontuários
- **THEN** a aplicação navega para a área correspondente se já estiver integrada e autorizada, sem habilitar ações administrativas ou clínicas novas no painel

### Requirement: Resumo diário do Profissional
A Visão geral do Profissional MUST obter as Consultas do dia por meio do contrato existente `GET /consultas`, respeitando integralmente o escopo aplicado pelo Xano. MUST apresentar totais de Consultas do dia, atendimentos realizados e Consultas confirmadas, além do horário e nome do Paciente da próxima Consulta ativa. MUST ordenar as Consultas por horário e apresentar no máximo cinco itens, exibindo somente horário, nome do Paciente e situação. MUST NOT solicitar dados de outras rotas nem exibir campos clínicos, de contato, motivo ou Procedimentos.

#### Scenario: Profissional acessa o resumo com Consultas
- **WHEN** um Profissional autenticado abre a Visão geral e o Xano retorna Consultas do dia no escopo autorizado
- **THEN** a tela mostra as métricas derivadas da resposta, a próxima Consulta ativa e até cinco Consultas em ordem de horário

#### Scenario: Próxima Consulta ativa
- **WHEN** existem Consultas futuras no dia com situação não terminal
- **THEN** a tela identifica como próxima a Consulta de menor horário e exclui Consultas realizadas, canceladas ou marcadas como falta

#### Scenario: Dia sem Consultas
- **WHEN** o Xano retorna uma lista vazia para o dia
- **THEN** a tela mostra as métricas zeradas, informa que não há Consultas para hoje e mantém os atalhos existentes disponíveis

#### Scenario: Resposta inválida
- **WHEN** a resposta de Consultas não pode ser interpretada
- **THEN** a tela informa que não foi possível carregar a agenda e não mostra itens parciais ou dados de uma resposta anterior como atuais
