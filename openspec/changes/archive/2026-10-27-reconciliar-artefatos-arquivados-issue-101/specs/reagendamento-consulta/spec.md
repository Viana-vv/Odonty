# reagendamento consulta Specification

## Purpose

Restaurar na especificação vigente os requisitos aprovados nos deltas arquivados para a capacidade `reagendamento-consulta`.

## ADDED Requirements

### Requirement: Reagendamento administrativo autorizado

O sistema MUST aceitar reagendamento somente por Conta de Acesso ativa com perfil Administrador ou Recepcionista e sessão válida. O Paciente da nova Consulta MUST ser o mesmo da Consulta original. O Profissional MUST ser derivado da Disponibilidade escolhida no backend.

#### Scenario: Conta administrativa reagenda

- **WHEN** uma Conta administrativa autorizada informa uma Consulta Agendada ou Confirmada, outra Disponibilidade livre futura e justificativa válida
- **THEN** o sistema cria a nova Consulta Agendada para o mesmo Paciente e para o Profissional da Disponibilidade escolhida

#### Scenario: Sessão ausente ou expirada

- **WHEN** uma solicitação não possui sessão válida
- **THEN** o sistema retorna 401 sem alterar Consultas, Disponibilidades ou histórico

#### Scenario: Perfil sem permissão

- **WHEN** uma Conta sem perfil administrativo solicita reagendamento diretamente à API
- **THEN** o sistema retorna 403 sem alterar dados

### Requirement: Reagendamento atômico e sem conflito

O Xano MUST validar Paciente ativo, Profissional ativo, intervalo válido e futuro, Disponibilidade livre e ausência de sobreposição de Consultas ativas do Paciente ou Profissional. Cancelamento, auditoria, liberação do horário original quando ainda futuro e reserva/criação no horário novo MUST constituir uma única operação atômica. A Consulta original MUST ser desconsiderada somente na checagem do conflito com sua própria substituição. A mesma Disponibilidade original MUST NOT ser aceita como destino.

#### Scenario: Destino ocupado ou bloqueado

- **WHEN** a Disponibilidade escolhida está reservada, bloqueada, no passado ou conflita com outra Consulta ativa
- **THEN** o sistema retorna 409 e preserva integralmente Consulta e reserva originais

#### Scenario: Requisições simultâneas

- **WHEN** duas solicitações tentam reagendar a mesma Consulta ou reservar intervalos conflitantes
- **THEN** no máximo uma operação conclui, sem duplicação de Consulta ativa nem liberação indevida do horário anterior

#### Scenario: Falha na persistência

- **WHEN** uma falha acontece após iniciar a alteração dos dados
- **THEN** nenhuma mudança parcial de Consulta, histórico ou Disponibilidade permanece persistida

#### Scenario: Edição de Disponibilidade aguardava reserva concorrente

- **WHEN** uma edição de Disponibilidade inicia antes do reagendamento e só adquire a trava depois da reserva
- **THEN** a edição relê o estado e rejeita a escrita obsoleta com 409, preservando a Disponibilidade reservada

#### Scenario: Dados inválidos ou recurso inexistente

- **WHEN** identificadores não são inteiros positivos, a justificativa está vazia ou excede 1000 caracteres, existem campos não aceitos ou um recurso obrigatório não existe
- **THEN** o sistema retorna erro seguro de validação ou recurso não encontrado sem alterar dados

### Requirement: Seleção visual e resultado confirmado

A interface MUST seguir os padrões de Nova Consulta do kit Sorriso Mais, permitir selecionar Paciente, Consulta elegível, Profissional, data e horário livre e exigir justificativa. Sucesso MUST ser apresentado somente após confirmação da API. Falhas MUST apresentar mensagem compreensível e permitir nova tentativa; sessão expirada MUST limpar a credencial local.

#### Scenario: Seleção e confirmação

- **WHEN** uma Conta administrativa seleciona uma Consulta e informa horário e justificativa
- **THEN** a interface envia uma única operação de reagendamento e, após sucesso, atualiza as opções e mostra confirmação

#### Scenario: Mudança de filtros e erro

- **WHEN** o Paciente, a Consulta, o Profissional ou a data selecionada muda, ou a API informa conflito
- **THEN** a interface atualiza as opções dependentes sem enviar seleção obsoleta e não apresenta sucesso para operação rejeitada

#### Scenario: Listagem vazia ou indisponível

- **WHEN** não existem Consultas elegíveis ou horários livres, ou falha a leitura da API
- **THEN** a interface informa a condição e impede envio incompleto

### Requirement: Preservar a Consulta original e sua auditoria

O sistema MUST manter a Consulta original no histórico, com seu Paciente, Profissional, intervalo, Disponibilidade e relações anteriores preservados, alterando somente a situação de Agendada ou Confirmada para Cancelada. A transição MUST registrar justificativa, data e Conta de Acesso responsável. Um vínculo persistente explícito MUST identificar a Consulta original e a nova com justificativa, data e responsável; esse vínculo MUST ser criado na mesma transação das demais mudanças e permanecer imutável. Procedimentos, Exames e Registros Clínicos MUST permanecer na original sem cópia automática. O sistema MUST NOT reabrir situações finais nem reagendar Consulta Em atendimento.

#### Scenario: Preservação após sucesso

- **WHEN** o reagendamento é concluído
- **THEN** a Consulta original permanece Cancelada com a justificativa e o responsável na auditoria, a nova Consulta fica vinculada à Disponibilidade escolhida e uma relação persistente registra explicitamente ambas as Consultas

#### Scenario: Consulta encerrada ou em atendimento

- **WHEN** a Consulta está Cancelada, Realizada, Falta ou Em atendimento
- **THEN** o sistema rejeita o reagendamento com 409 sem criar nova Consulta

#### Scenario: Consulta legada sem vínculo suficiente

- **WHEN** não é possível identificar a Disponibilidade original de forma explícita
- **THEN** o sistema rejeita a operação sem inferir nem migrar vínculos históricos

