# Spec Delta

## Purpose

Permite que Administração e Recepção registrem pela Agenda os intervalos em que um Profissional pode receber Consultas, com confirmação do resultado e respeito às regras de acesso e conflito.

## ADDED Requirements

### Requirement: Cadastro de Disponibilidade pela Agenda
O sistema SHALL permitir que Administração e Recepção cadastrem uma Disponibilidade para um Profissional ativo informando data, horário inicial e horário final. Cada envio SHALL representar um único intervalo.

#### Scenario: Cadastrar intervalo válido
- **WHEN** Administração ou Recepção informa um Profissional ativo e um intervalo válido aceito pelo Xano
- **THEN** o sistema confirma o cadastro e atualiza a Agenda para refletir a nova Disponibilidade

#### Scenario: Xano confirma o cadastro com resposta mínima
- **WHEN** o Xano responde HTTP 201 com identificador, Profissional e início, mas omite o fim ou a situação
- **THEN** o sistema completa esses campos com o intervalo enviado e a situação `disponivel`, confirma o cadastro e atualiza a Agenda

#### Scenario: Campos ausentes ou intervalo inválido
- **WHEN** a pessoa deixa um campo obrigatório sem preencher ou informa um intervalo inválido
- **THEN** o sistema orienta a correção e não apresenta o cadastro como concluído

#### Scenario: Intervalo em conflito
- **WHEN** o Xano rejeita o intervalo por conflito com outra Disponibilidade ou Consulta
- **THEN** o sistema informa que o horário não pôde ser cadastrado e permite corrigir os dados sem alegar sucesso

#### Scenario: Falha ou resposta inválida da API
- **WHEN** a API falha, fica indisponível ou retorna uma resposta incompatível
- **THEN** o sistema informa que não foi possível concluir o cadastro e mantém a possibilidade de tentar novamente

### Requirement: Opções de Profissional e autorização
O sistema SHALL apresentar Profissionais ativos como opções de cadastro somente para Administração e Recepção. A autorização SHALL ser validada pelo Xano em cada operação, independentemente dos controles exibidos pela interface.

#### Scenario: Carregar profissionais ativos
- **WHEN** Administração ou Recepção abre o formulário de Disponibilidade
- **THEN** o sistema permite selecionar um Profissional ativo e informa quando nenhuma opção puder ser carregada

#### Scenario: Perfil sem permissão
- **WHEN** uma Conta de Acesso sem permissão tenta cadastrar uma Disponibilidade
- **THEN** o Xano rejeita a operação e o sistema informa falta de autorização sem confirmar o cadastro
