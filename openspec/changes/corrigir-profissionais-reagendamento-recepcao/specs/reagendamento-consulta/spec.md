## ADDED Requirements

### Requirement: Seleções independentes das opções de agendamento
A tela de Reagendar Consulta SHALL carregar Pacientes e Profissionais por suas rotas próprias, sem consultar Procedimentos ou GET `/agenda/opcoes`. O seletor de destino SHALL oferecer somente Profissionais ativos com nome, CRO e especialidade preenchidos e SHALL informar quando cadastros incompletos forem omitidos das opções.

#### Scenario: Recepcionista abre com cadastro incompleto
- **WHEN** a Recepcionista abre Reagendar Consulta e existe um Profissional ativo incompleto junto de outros válidos
- **THEN** a tela permite selecionar Paciente e Consulta e escolher um Profissional válido, sem falha geral

#### Scenario: Opções da Agenda indisponíveis
- **WHEN** GET `/agenda/opcoes` falha e as rotas próprias estão disponíveis
- **THEN** o carregamento do reagendamento permanece funcional

#### Scenario: Lista sem destino válido
- **WHEN** não existem Profissionais ativos com cadastro completo
- **THEN** a tela informa a ausência de opções e impede envio incompleto

#### Scenario: Sessão ou permissão recusada
- **WHEN** uma das leituras retorna 401 ou 403
- **THEN** a tela trata o acesso recusado e não envia reagendamento
