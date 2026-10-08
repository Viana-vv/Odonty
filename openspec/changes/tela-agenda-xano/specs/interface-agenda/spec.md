## ADDED Requirements

### Requirement: Navegação diária conectada
A interface MUST apresentar a Agenda conectada em lista diária, com seletor de data, navegação entre dias, filtro por situação e busca por Paciente ou Procedimento. A lista MUST ser ordenada por horário e seguir a referência visual aprovada do kit Sorriso Mais. MUST NOT exibir telefone, documentos pessoais ou dados clínicos.

#### Scenario: Equipe abre a Agenda
- **WHEN** Administrador, Recepcionista ou Profissional acessa Agenda no modo conectado
- **THEN** a interface carrega Consultas do dia selecionado, no escopo do Xano, com filtros e ordenação

#### Scenario: Dia sem Consultas
- **WHEN** não existem Consultas para o dia e filtros selecionados
- **THEN** a interface informa estado vazio e mantém busca, data e filtros utilizáveis

#### Scenario: Falha ao carregar Agenda
- **WHEN** a API falha ou a sessão expira
- **THEN** a interface apresenta mensagem compreensível e não mostra dados desatualizados como atuais

### Requirement: Agendamento administrativo pela Agenda
A interface MUST permitir que Administrador e Recepcionista abram formulário e selecionem Paciente ativo, Profissional ativo, data da Consulta, Disponibilidade livre, zero ou mais Procedimentos ativos e motivo administrativo opcional. Paciente, Profissional, data e Disponibilidade são obrigatórios. A data da Consulta MUST ser selecionada dentro do formulário e MUST ser independente do filtro diário da Agenda até a conclusão do agendamento. A lista de Disponibilidades MUST corresponder ao Profissional e à data selecionados no formulário. A Agenda só é atualizada após confirmação do Xano.

A interface MUST manter no máximo um formulário de ação da Agenda aberto por vez. Abrir o formulário de Disponibilidade MUST fechar o formulário de Consulta, e abrir o formulário de Consulta MUST fechar o formulário de Disponibilidade.

#### Scenario: Agendamento concluído
- **WHEN** a equipe envia formulário válido e o Xano confirma a criação
- **THEN** a interface confirma sucesso e atualiza a Agenda do dia da Disponibilidade

#### Scenario: Data da Consulta independente do filtro diário
- **WHEN** a equipe escolhe uma data no formulário diferente da data selecionada para filtrar a Agenda
- **THEN** a lista de horários usa a data do formulário e o filtro diário permanece inalterado; após o agendamento confirmado, a Agenda passa a mostrar o dia da Consulta criada

#### Scenario: Alternar formulários da Agenda
- **WHEN** a equipe abre um formulário enquanto o outro está aberto
- **THEN** somente o formulário recém-aberto permanece visível

#### Scenario: Conflito de disponibilidade
- **WHEN** outro agendamento ocupa o horário antes do envio
- **THEN** a interface informa conflito e permite selecionar outra Disponibilidade

#### Scenario: Profissional tenta agendar
- **WHEN** um Profissional acessa Agenda
- **THEN** a interface não oferece o comando para criar Consulta

### Requirement: Transições de situação da Consulta
A interface MUST oferecer somente transições permitidas ao perfil autenticado pelo contrato do Xano. Cancelamento MUST exigir motivo e confirmação. Em caso de falha, a situação exibida permanece a persistida; após sucesso, a interface recarrega a lista.

#### Scenario: Cancelamento sem motivo
- **WHEN** a equipe tenta confirmar cancelamento sem motivo
- **THEN** a interface exige motivo e não envia a alteração

#### Scenario: Transição não permitida
- **WHEN** o Xano nega mudança de situação
- **THEN** a interface informa que a situação não foi alterada e recarrega o estado persistido

#### Scenario: Atualização de situação sem cartões repetidos
- **WHEN** o Profissional atualiza uma Consulta para Em atendimento e o Xano confirma
- **THEN** a interface carrega a lista uma vez, mostra cada Consulta uma vez com a situação persistida e oferece Realizada como próxima transição da Consulta atualizada
