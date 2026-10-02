## Purpose

Define operações REST autorizadas para disponibilidades da Agenda e Consultas, evitando conflitos de horário e preservando os vínculos e o histórico do atendimento.

## ADDED Requirements

### Requirement: Consultar disponibilidades da Agenda
O sistema MUST permitir consultar Disponibilidades da Agenda futuras que estejam livres, filtradas por Profissional e período. A resposta MUST excluir horários bloqueados, reservados, passados e Profissionais inativos.

#### Scenario: Listar horários disponíveis
- **WHEN** uma Conta de Acesso autenticada consulta um período válido
- **THEN** o sistema retorna apenas disponibilidades futuras e livres dos Profissionais ativos no período solicitado

#### Scenario: Rejeitar período inválido
- **WHEN** a data final antecede a data inicial ou os filtros possuem formato inválido
- **THEN** o sistema retorna erro de validação sem consultar ou alterar dados

### Requirement: Administrar Disponibilidades da Agenda
O sistema MUST permitir que um Profissional ativo administre apenas suas próprias disponibilidades e que Administrador ou Recepcionista administrem disponibilidades conforme sua permissão. O início MUST anteceder o fim e não pode haver sobreposição para o mesmo Profissional.

#### Scenario: Criar disponibilidade válida
- **WHEN** um Profissional ativo ou uma Conta de Acesso administrativa autorizada envia um intervalo válido sem sobreposição
- **THEN** o sistema cria a Disponibilidade da Agenda e a associa ao Profissional permitido

#### Scenario: Rejeitar sobreposição
- **WHEN** a nova disponibilidade se sobrepõe a outra do mesmo Profissional
- **THEN** o sistema rejeita a operação sem criar intervalo parcial

#### Scenario: Impedir alteração da agenda de outro Profissional
- **WHEN** um Profissional tenta criar ou alterar disponibilidade de outro Profissional
- **THEN** o sistema retorna acesso negado sem modificar a Agenda

### Requirement: Agendar Consulta sem conflito
O sistema MUST criar uma Consulta somente para Paciente, Profissional ativo e Disponibilidade futura livre, com todos os vínculos consistentes. A reserva do horário e a criação da Consulta MUST ser atômicas. O sistema MUST rejeitar conflito de Consulta para o mesmo Profissional ou Paciente e horário.

#### Scenario: Agendar em disponibilidade livre
- **WHEN** Paciente agenda para si ou uma Conta de Acesso administrativa agenda em seu escopo uma disponibilidade válida e livre
- **THEN** o sistema cria a Consulta e reserva a Disponibilidade na mesma operação

#### Scenario: Duas tentativas concorrentes
- **WHEN** duas requisições tentam reservar a mesma disponibilidade ao mesmo tempo
- **THEN** no máximo uma Consulta é criada e a outra recebe conflito sem dados parciais

#### Scenario: Rejeitar vínculo ou horário inválido
- **WHEN** a disponibilidade não pertence ao Profissional, está bloqueada/reservada, é passada ou conflita com outra Consulta ativa
- **THEN** o sistema rejeita a operação sem alterar Consulta ou Disponibilidade

### Requirement: Consultar e atualizar Consultas por perfil
O sistema MUST listar Consultas conforme o escopo do perfil autenticado: Paciente apenas as próprias, Profissional apenas as de sua atuação autorizada e Administrador/Recepcionista conforme permissões administrativas. Atualizações de situação MUST respeitar as transições permitidas e não podem apagar o histórico.

#### Scenario: Listar consultas no escopo permitido
- **WHEN** uma Conta de Acesso autenticada solicita Consultas
- **THEN** o sistema retorna somente Consultas que essa Conta de Acesso pode consultar e não inclui informações clínicas em listagens administrativas

#### Scenario: Bloquear consulta de outro paciente ou profissional
- **WHEN** uma Conta de Acesso tenta consultar ou atualizar uma Consulta fora do seu escopo
- **THEN** o sistema retorna acesso negado sem revelar se o registro existe

#### Scenario: Preservar consulta cancelada
- **WHEN** uma Conta de Acesso autorizada cancela uma Consulta conforme a regra vigente
- **THEN** a Consulta continua no histórico com situação, responsável, data e motivo do cancelamento

### Requirement: Proteger contratos de Agenda e Consulta
Todas as operações protegidas MUST validar sessão, situação da Conta de Acesso e autorização no Xano. Respostas não podem expor credenciais ou detalhes internos; requisições e respostas não podem registrar dados clínicos em histórico ou logs.

#### Scenario: Requisição sem sessão válida
- **WHEN** uma operação protegida é chamada sem sessão, com sessão expirada ou revogada
- **THEN** o sistema retorna não autenticado sem executar a operação

#### Scenario: Falha interna
- **WHEN** ocorre erro inesperado no backend
- **THEN** o sistema retorna mensagem segura, não expõe dados sensíveis e não deixa alterações parciais
