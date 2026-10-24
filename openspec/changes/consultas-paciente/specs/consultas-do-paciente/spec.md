# Consultas do Paciente

## Requisitos

### Requirement: Consultar Consultas próprias
O sistema MUST permitir que o Paciente visualize suas Consultas futuras e passadas usando a sessão autenticada e o escopo garantido pelo Xano.

#### Scenario: Consultas carregadas
- WHEN a tela é aberta com sessão autenticada
- THEN solicita a lista pelo GET /consultas sem informar paciente_id
- AND organiza os itens entre futuras e passadas
- AND apresenta data, horário, Profissional e situação
- AND não apresenta procedimentos ou informação clínica

#### Scenario: Lista vazia ou falha
- WHEN não há Consultas ou a API falha
- THEN informa lista vazia ou erro em linguagem simples

#### Scenario: Solicitar cancelamento
- WHEN a pessoa consulta uma Consulta futura
- THEN a tela informa que cancelamento deve ser solicitado à clínica
- AND não oferece ação de agendar ou cancelar
