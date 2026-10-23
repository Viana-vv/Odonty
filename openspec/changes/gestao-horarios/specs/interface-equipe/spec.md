## MODIFIED Requirements

### Requirement: Visualizar Disponibilidades na Agenda

A Agenda MUST apresentar, junto às consultas do dia selecionado, os horários futuros de Disponibilidade retornados para o período, identificando Profissional, início, fim e situação. A lista MUST incluir horários livres e bloqueados para permitir a manutenção, sem incluir horários reservados ou indisponíveis.

#### Scenario: Exibição de horários do dia

- WHEN a Conta de Acesso autorizada abre a Agenda em uma data com horários futuros
- THEN a interface apresenta cada Disponibilidade livre ou bloqueada com Profissional, intervalo e situação

#### Scenario: Dia sem horários

- WHEN não existem Disponibilidades livres ou bloqueadas no período
- THEN a Agenda informa que não há horários para exibir sem apresentar erro

#### Scenario: Falha ao consultar horários

- WHEN a API rejeita a leitura ou está indisponível
- THEN a Agenda mostra mensagem compreensível e não indica lista vazia como sucesso

### Requirement: Manter Disponibilidades pela Agenda

A Agenda MUST permitir que Profissional, Administrador ou Recepcionista autorizados editem o intervalo de uma Disponibilidade futura livre ou bloqueada e bloqueiem ou desbloqueiem esses horários. A operação MUST usar a API existente e MUST apresentar confirmação somente após sucesso. O Xano MUST validar autenticação, autorização, escopo do Profissional, estado do horário, formato do intervalo e conflitos com outras Disponibilidades. Horários reservados, indisponíveis ou passados MUST permanecer inalterados.

#### Scenario: Editar intervalo sem conflito

- WHEN uma Conta de Acesso autorizada salva um intervalo futuro válido sem sobreposição
- THEN a API atualiza a Disponibilidade e a Agenda apresenta o novo intervalo após confirmação

#### Scenario: Bloquear e desbloquear horário

- WHEN uma Conta de Acesso autorizada bloqueia uma Disponibilidade livre ou desbloqueia uma bloqueada
- THEN a API atualiza a situação e a Agenda apresenta a situação confirmada pelo Xano

#### Scenario: Conflito de horário

- WHEN o intervalo informado se sobrepõe a outra Disponibilidade do Profissional
- THEN o Xano rejeita a operação e a Agenda informa o conflito sem exibir sucesso

#### Scenario: Horário reservado, passado ou inexistente

- WHEN a Conta de Acesso tenta alterar uma Disponibilidade reservada, passada, indisponível ou inexistente
- THEN o Xano rejeita a operação e a Agenda informa que não foi possível atualizar

#### Scenario: Conta sem autorização ou Profissional fora do escopo

- WHEN uma Conta de Acesso não autorizada ou um Profissional tenta alterar horário de outro Profissional
- THEN o Xano rejeita a operação e nenhum dado é alterado
