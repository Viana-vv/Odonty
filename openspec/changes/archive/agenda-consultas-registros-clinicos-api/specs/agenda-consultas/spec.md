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
O sistema MUST criar uma Consulta somente por solicitação de Administrador ou Recepcionista autorizados, para Paciente ativo, Profissional ativo e Disponibilidade futura livre, com todos os vínculos consistentes. O Paciente MUST NOT agendar a própria Consulta pelo sistema. `procedimento_ids` pode ser vazio; quando houver IDs, todos MUST referenciar Procedimentos ativos e sem duplicatas. A reserva do horário e a criação da Consulta MUST ser atômicas. O sistema MUST rejeitar conflito de Consulta para o mesmo Profissional ou Paciente e horário.

#### Scenario: Equipe administrativa agenda em disponibilidade livre
- **WHEN** Administrador ou Recepcionista autorizado agenda para um Paciente ativo uma disponibilidade válida e livre
- **THEN** o sistema cria a Consulta e reserva a Disponibilidade na mesma operação

#### Scenario: Impedir agendamento pelo Paciente
- **WHEN** Paciente autenticado tenta criar uma Consulta para si ou para outro Paciente
- **THEN** o sistema nega a operação sem criar Consulta nem reservar Disponibilidade

#### Scenario: Agendar Consulta sem Procedimento
- **WHEN** Administrador ou Recepcionista autorizado agenda uma Consulta com `procedimento_ids` vazio
- **THEN** o sistema cria a Consulta sem Procedimento e preserva `procedimento_id` legado como nulo

#### Scenario: Rejeitar Procedimentos inválidos
- **WHEN** a lista contém Procedimento inexistente, inativo ou duplicado
- **THEN** o sistema rejeita o agendamento sem criar Consulta, vínculos parciais ou reserva

#### Scenario: Duas tentativas concorrentes
- **WHEN** duas requisições tentam reservar a mesma disponibilidade ao mesmo tempo
- **THEN** no máximo uma Consulta é criada e a outra recebe conflito sem dados parciais

#### Scenario: Reutilizar horário após cancelamento
- **WHEN** uma Consulta futura é cancelada por Conta de Acesso autorizada e o mesmo horário é agendado novamente
- **THEN** o sistema preserva a Consulta cancelada e seu vínculo histórico, libera a Disponibilidade e associa a nova Consulta ao mesmo horário sem conflito

#### Scenario: Rejeitar vínculo ou horário inválido
- **WHEN** a disponibilidade não pertence ao Profissional, está bloqueada/reservada, é passada ou conflita com outra Consulta ativa
- **THEN** o sistema rejeita a operação sem alterar Consulta ou Disponibilidade

### Requirement: Consultar e atualizar Consultas por perfil
O sistema MUST listar Consultas conforme o escopo do perfil autenticado: Paciente pode consultar suas Consultas passadas e futuras; Profissional consulta as de sua atuação autorizada; Administrador/Recepcionista consultam conforme permissões administrativas. O Xano MUST derivar o Paciente da sessão e não confiar em `paciente_id` enviado pelo perfil Paciente. Atualizações de situação MUST respeitar as transições e permissões definidas e não podem apagar o histórico. Paciente MUST NOT cancelar nem alterar situação de Consulta pelo sistema; solicitações de cancelamento são comunicadas à clínica fora do sistema.

#### Scenario: Listar consultas no escopo permitido
- **WHEN** uma Conta de Acesso autenticada solicita Consultas
- **THEN** o sistema retorna somente Consultas que essa Conta de Acesso pode consultar e não inclui informações clínicas em listagens administrativas

#### Scenario: Paciente consulta Consultas próprias
- **WHEN** Paciente autenticado consulta suas Consultas sem filtro ou envia filtro `paciente_id` divergente
- **THEN** o sistema retorna somente suas Consultas passadas e futuras, ignorando ou rejeitando o identificador divergente sem revelar dados de terceiros

#### Scenario: Bloquear consulta de outro paciente ou profissional
- **WHEN** uma Conta de Acesso tenta consultar ou atualizar uma Consulta fora do seu escopo
- **THEN** o sistema retorna acesso negado sem revelar se o registro existe

#### Scenario: Impedir cancelamento pelo Paciente
- **WHEN** Paciente tenta alterar a situação ou cancelar uma Consulta própria
- **THEN** o sistema nega a operação e mantém Consulta e Disponibilidade inalteradas

#### Scenario: Preservar consulta cancelada
- **WHEN** uma Conta de Acesso autorizada cancela uma Consulta conforme a regra vigente
- **THEN** a Consulta continua no histórico com situação, responsável, data e motivo registrados em histórico append-only e a Disponibilidade futura é liberada para novo agendamento sem remover o vínculo da Consulta cancelada

#### Scenario: Aplicar transições e responsáveis permitidos
- **WHEN** Profissional ou equipe administrativa autorizada altera a situação de Consulta
- **THEN** o Xano aceita somente `agendada → confirmada/cancelada`, `confirmada → em atendimento/cancelada/falta` ou `em atendimento → realizada`; somente Profissional autorizado inicia atendimento, conclui ou registra falta
- **AND** transições inválidas e tentativas de reabrir estado final são rejeitadas sem alterar o histórico

### Requirement: Alterar Disponibilidade livre
O sistema MUST permitir PATCH de intervalo e situação somente em Disponibilidade futura livre e dentro do escopo autorizado. O PATCH MUST aceitar situação `disponível` ou `bloqueado`, respeitar `inicio < fim` e rejeitar sobreposição. Disponibilidade reservada ou controlada pelo fluxo de agendamento não pode ser liberada ou editada diretamente.

#### Scenario: Bloquear ou desbloquear intervalo livre
- **WHEN** Profissional autorizado ou equipe administrativa autorizada altera intervalo livre futuro sem sobreposição ou alterna sua situação entre disponível e bloqueado
- **THEN** o sistema atualiza a Disponibilidade e retorna o recurso atualizado

#### Scenario: Impedir alteração direta de intervalo reservado
- **WHEN** uma Conta de Acesso tenta alterar ou liberar Disponibilidade reservada
- **THEN** o sistema rejeita a operação sem alterar Consulta ou Disponibilidade

### Requirement: Proteger contratos de Agenda e Consulta
Todas as operações protegidas MUST validar sessão, situação da Conta de Acesso e autorização no Xano. Respostas não podem expor credenciais ou detalhes internos; requisições e respostas não podem registrar dados clínicos em histórico ou logs.

Respostas de sucesso MUST usar as chaves de recurso definidas no design. Respostas de erro MUST usar `{ "codigo": "<código estável>", "mensagem": "<mensagem segura>" }`, com HTTP 400 para validação, 401 para sessão, 403 para perfil sem permissão, 404 para recurso inexistente ou fora do escopo e 409 para conflito. Mensagens MUST ser sanitizadas e não podem confirmar a existência de recursos fora do escopo.

#### Scenario: Representar Consulta realizada sem alterar o enum legado
- **WHEN** uma Consulta armazenada com situação legada `Concluída` é retornada pela API
- **THEN** o sistema apresenta a situação `Realizada` e preserva o valor armazenado no Xano

#### Scenario: Requisição sem sessão válida
- **WHEN** uma operação protegida é chamada sem sessão, com sessão expirada ou revogada
- **THEN** o sistema retorna não autenticado sem executar a operação

#### Scenario: Falha interna
- **WHEN** ocorre erro inesperado no backend
- **THEN** o sistema retorna mensagem segura, não expõe dados sensíveis e não deixa alterações parciais
