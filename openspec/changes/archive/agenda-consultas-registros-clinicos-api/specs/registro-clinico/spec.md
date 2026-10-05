## Purpose

Define o registro clínico longitudinal do Paciente separado da Consulta e do Prontuário, com autoria profissional, vínculo validado e acesso restrito.

## ADDED Requirements

### Requirement: Criar Registro Clínico vinculado
O sistema MUST permitir que Profissional ativo e autorizado crie Registro Clínico associado ao Prontuário do Paciente e, quando informado, à Consulta correspondente. O Paciente, Profissional, Prontuário e Consulta relacionados MUST ser compatíveis.

#### Scenario: Criar registro para atendimento próprio
- **WHEN** Profissional autorizado registra informações de uma Consulta que pertence ao Paciente e ao próprio Profissional
- **THEN** o sistema cria Registro Clínico com autoria e data identificadas no Prontuário correto

#### Scenario: Rejeitar vínculos inconsistentes
- **WHEN** o Registro Clínico referencia Consulta, Paciente ou Prontuário incompatíveis
- **THEN** o sistema rejeita a operação sem gravar um registro parcial

#### Scenario: Impedir criação por perfil administrativo
- **WHEN** Administrador ou Recepcionista tenta criar Registro Clínico sem perfil profissional autorizado
- **THEN** o sistema retorna acesso negado sem alterar o histórico clínico

### Requirement: Consultar Registros Clínicos com autorização
O sistema MUST permitir a consulta de Registros Clínicos somente conforme as permissões do domínio: Profissional autorizado acessa os registros necessários ao atendimento; Paciente acessa somente os próprios conteúdos liberados pela clínica; Administrador e Recepcionista não recebem acesso clínico por sua função administrativa.

#### Scenario: Profissional consulta registro necessário
- **WHEN** um Profissional ativo autorizado consulta registro de Paciente sob seu escopo de atendimento
- **THEN** o sistema retorna somente os Registros Clínicos permitidos

#### Scenario: Paciente consulta conteúdo liberado do próprio prontuário
- **WHEN** Paciente autenticado consulta informações clínicas próprias liberadas pela clínica
- **THEN** o sistema retorna somente o conteúdo liberado para esse Paciente

#### Scenario: Impedir acesso clínico não autorizado
- **WHEN** uma Conta de Acesso consulta Registro Clínico fora do próprio escopo ou sem permissão clínica
- **THEN** o sistema nega o acesso sem confirmar a existência do registro

### Requirement: Preservar histórico clínico
Registros Clínicos concluídos MUST permanecer no histórico e não podem ser removidos ou sobrescritos. Correções autorizadas MUST preservar o conteúdo anterior, o autor, a data e a justificativa da alteração.

#### Scenario: Corrigir registro concluído
- **WHEN** Profissional autorizado solicita correção de Registro Clínico concluído
- **THEN** o sistema registra retificação vinculada ao original, mantém o conteúdo anterior auditável e herda o valor de `liberado_paciente` do original sem ampliar a visibilidade

#### Scenario: Impedir exclusão de registro concluído
- **WHEN** qualquer operação tenta excluir ou substituir Registro Clínico concluído
- **THEN** o sistema rejeita a operação e preserva o histórico

### Requirement: Proteger dados clínicos
Operações de Registro Clínico MUST validar sessão e autorização no Xano, usar respostas sem cache e não registrar conteúdo clínico em logs, histórico de requisições ou mensagens técnicas.

#### Scenario: Requisição sem autorização
- **WHEN** uma Conta de Acesso não autenticada, inativa ou sem permissão tenta acessar ou alterar Registros Clínicos
- **THEN** o sistema rejeita a operação sem expor dados clínicos

#### Scenario: Falha interna durante gravação
- **WHEN** ocorre falha ao criar ou corrigir um Registro Clínico
- **THEN** o sistema retorna erro seguro e não deixa registro parcial nem conteúdo clínico nos logs
