# consultas Specification

## Purpose
Restaurar na especificação vigente os requisitos aprovados nos deltas arquivados para a capacidade `consultas`.

## Requirements

### Requirement: Compatibilidade da resposta de Consultas para equipe
O endpoint `GET /consultas` MUST preservar o formato de resposta existente para os perfis Profissional, Administrador e Recepcionista, sujeito ao escopo e às permissões já aplicados no Xano.

#### Scenario: Equipe consulta Consultas
- **WHEN** uma Conta de Acesso autorizada com perfil Profissional, Administrador ou Recepcionista consulta `GET /consultas`
- **THEN** o endpoint retorna os campos administrativos e de Procedimentos já suportados pelo contrato atual
- **AND** filtros, escopo e ordenação existentes continuam aplicados

#### Scenario: Requisição sem autenticação válida
- **WHEN** uma Conta de Acesso sem sessão válida solicita `GET /consultas`
- **THEN** o Xano rejeita a requisição segundo o comportamento de autenticação existente

### Requirement: Resposta mínima de Consultas para Paciente
O endpoint `GET /consultas` MUST retornar ao perfil Paciente somente os dados administrativos mínimos das próprias Consultas: identificadores da Consulta, Paciente e Profissional, início, fim, situação e nome do Profissional. A resposta MUST omitir nome e identificador de Procedimentos, nome do Paciente, identificador de disponibilidade e quaisquer campos internos ou adicionais destinados à equipe.

#### Scenario: Paciente consulta as próprias Consultas
- **WHEN** uma Conta de Acesso ativa com perfil Paciente consulta `GET /consultas`
- **THEN** o Xano limita os resultados às Consultas do Paciente associado à Conta de Acesso
- **AND** cada item contém apenas os campos mínimos para Paciente, incluindo o nome do Profissional
- **AND** nenhum campo de Procedimento ou campo interno da equipe é retornado

#### Scenario: Paciente não possui Consultas
- **WHEN** uma Conta de Acesso ativa com perfil Paciente consulta `GET /consultas` e não possui Consultas
- **THEN** o endpoint retorna uma lista vazia no formato de resposta do contrato
