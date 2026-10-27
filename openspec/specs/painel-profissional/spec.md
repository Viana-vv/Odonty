# painel-profissional Specification

## Purpose
Restaurar na especificação vigente os requisitos aprovados nos deltas arquivados para a capacidade `painel-profissional`.

## Requirements

### Requirement: Consultar visão geral diária
O sistema MUST apresentar ao Profissional autenticado uma visão geral com Consultas do dia obtidas pelo contrato Xano existente, com horário, Paciente, situação e procedimentos retornados pelo contrato. Indicadores MUST ser derivados somente da resposta. A tela MUST oferecer navegação para Agenda e Prontuário sem contornar controles de acesso.

#### Scenario: Profissional possui Consultas no dia
- **WHEN** o Profissional abre a visão geral com sessão válida e o Xano retorna Consultas do dia
- **THEN** o sistema mostra o total, atendimentos realizados, próxima Consulta e a lista ordenada por horário
- **AND** apresenta somente dados de agenda previstos no contrato, sem conteúdo de Registro Clínico

#### Scenario: Nenhuma Consulta no dia
- **WHEN** o Xano retorna uma lista vazia
- **THEN** o painel informa que não há Consultas para o dia e preserva os acessos à Agenda e ao Prontuário

#### Scenario: Sessão inválida ou sem permissão
- **WHEN** a API retorna não autenticado ou acesso negado
- **THEN** o sistema encerra a sessão local e informa que é necessário entrar novamente ou que o perfil não possui acesso

#### Scenario: Falha ao consultar a API
- **WHEN** ocorre falha de conexão ou resposta inválida
- **THEN** o sistema mostra mensagem segura e opção de tentar novamente, sem exibir detalhes internos
