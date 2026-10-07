## ADDED Requirements

### Requirement: Consulta administrativa da agenda
O Xano MUST fornecer dados administrativos mínimos para a Agenda, aplicar escopo por Conta de Acesso e preservar histórico. A lista MUST incluir identificadores, nomes de exibição de Paciente e Profissional, início, fim, situação, disponibilidade e nomes dos Procedimentos vinculados, sem telefone, documento pessoal, observações clínicas ou prontuário.
Os campos de data e hora MUST ser serializados como texto ISO 8601 com fuso horário.

#### Scenario: Equipe consulta a agenda diária
- **WHEN** Administrador ou Recepcionista consulta Consultas em um período
- **THEN** o Xano retorna Consultas dentro do escopo solicitado com dados administrativos mínimos

#### Scenario: Profissional consulta sua agenda
- **WHEN** um Profissional consulta Consultas
- **THEN** o Xano limita os resultados às Consultas do Profissional autenticado

#### Scenario: Conta sem autorização consulta a agenda
- **WHEN** uma Conta de Acesso sem perfil ou vínculo válido consulta a Agenda
- **THEN** o Xano nega a operação sem retornar dados de Paciente

### Requirement: Opções protegidas de agendamento
O Xano MUST fornecer a Administrador e Recepcionista opções ativas de Paciente, Profissional e Procedimento, limitadas a identificador e nome. Cadastros inativos e Profissionais afastados MUST NOT ser elegíveis.

#### Scenario: Recepção carrega opções do formulário
- **WHEN** uma Recepcionista autenticada solicita as opções
- **THEN** o Xano retorna somente cadastros ativos sem CPF, telefone, e-mail ou dado clínico

#### Scenario: Profissional solicita opções administrativas
- **WHEN** um Profissional solicita opções do formulário
- **THEN** o Xano retorna acesso negado

### Requirement: Integridade do agendamento
O Xano MUST permitir Consulta sem Procedimentos ou com vários Procedimentos ativos, vincular a Consulta à Disponibilidade e impedir reserva dupla e conflito de horário ou Paciente dentro de transação. Cancelamento MUST liberar a Disponibilidade e preservar Consulta e histórico.

#### Scenario: Agendamento com zero ou múltiplos procedimentos
- **WHEN** a equipe agenda Paciente ativo em Disponibilidade livre de Profissional ativo com zero ou mais Procedimentos ativos
- **THEN** o Xano cria Consulta e vínculos de Procedimento atomicamente

#### Scenario: Horário reservado simultaneamente
- **WHEN** solicitações concorrentes tentam usar horário ou período conflitante
- **THEN** no máximo uma Consulta ativa é criada e a outra recebe conflito
