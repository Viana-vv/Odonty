# edicao paciente Specification

## Purpose

Restaurar na especificação vigente os requisitos aprovados nos deltas arquivados para a capacidade `edicao-paciente`.

## ADDED Requirements

### Requirement: Preservação dos dados históricos e clínicos
O sistema SHALL alterar somente os campos cadastrais permitidos e SHALL preservar o identificador do Paciente, seu Prontuário, Consultas, Registros Clínicos, Procedimentos e Exames vinculados. A interface administrativa SHALL NOT exibir nem permitir editar observações de saúde ou outros dados clínicos.

#### Scenario: Atualização preserva histórico
- **WHEN** uma edição cadastral é concluída para Paciente com histórico vinculado
- **THEN** os relacionamentos e registros históricos permanecem intactos e somente os campos cadastrais autorizados são alterados

#### Scenario: Campo clínico enviado diretamente
- **WHEN** a chamada de edição inclui observações de saúde, conteúdo clínico ou outro campo fora da lista permitida
- **THEN** o backend rejeita a chamada sem retornar ou modificar esse conteúdo

### Requirement: Consulta e edição cadastral pela equipe
O sistema SHALL permitir que Administrador ou Recepcionista ativos, com sessão válida, consultem e atualizem os dados cadastrais permitidos de um Paciente existente. O backend SHALL validar a autorização e os dados em cada requisição e SHALL preservar prontuário, consultas e histórico clínico.

#### Scenario: Recepcionista abre e salva uma edição válida
- **WHEN** uma Recepcionista ativa consulta um Paciente existente e envia os seis campos cadastrais válidos
- **THEN** a API retorna os dados cadastrais permitidos, confirma a atualização e a interface fecha o formulário mostrando os dados atualizados

#### Scenario: Administrador edita os mesmos campos permitidos
- **WHEN** um Administrador ativo edita os dados cadastrais válidos de um Paciente existente
- **THEN** o sistema confirma a atualização sem modificar registros clínicos ou históricos

#### Scenario: Recepcionista completa um cadastro antigo
- **WHEN** uma Recepcionista abre um Paciente existente cujo CPF, celular ou e-mail está vazio
- **THEN** a interface abre o formulário com os valores disponíveis e permite preencher os campos faltantes
- **AND** o salvamento exige os mesmos dados válidos de uma atualização cadastral completa
- **AND** após salvar, o modal fecha, a listagem é atualizada e a edição pode ser reaberta com os dados persistidos

#### Scenario: Conta sem permissão tenta consultar ou editar
- **WHEN** uma Conta de Acesso sem perfil autorizado ou com sessão inválida chama diretamente as rotas
- **THEN** o Xano nega a operação sem revelar dados pessoais ou gravar alterações

#### Scenario: Dados inválidos ou CPF duplicado
- **WHEN** a equipe envia campos incompletos, inválidos ou CPF já utilizado
- **THEN** a API rejeita a atualização com erro seguro e mantém o Paciente inalterado

### Requirement: Consulta cadastral individual autorizada
O sistema SHALL permitir que Administrador ou Recepcionista ativos, com sessão válida, consultem os dados cadastrais de um Paciente pelo identificador. O backend SHALL retornar somente identificador, nome, data de nascimento, CPF, telefone, celular e e-mail; SHALL NOT retornar observações, dados clínicos, situação interna, prontuário ou histórico. Paciente inexistente SHALL receber resposta segura de recurso não encontrado.

#### Scenario: Equipe consulta Paciente
- **WHEN** Administrador ou Recepcionista ativo solicita Paciente existente com sessão válida
- **THEN** o sistema retorna somente os campos cadastrais permitidos para preencher o formulário

#### Scenario: Conta ou sessão sem autorização
- **WHEN** uma conta não autenticada, inativa, expirada, revogada, Paciente ou Profissional solicita os dados
- **THEN** o backend nega a operação sem retornar dados pessoais

#### Scenario: Paciente inexistente
- **WHEN** equipe autorizada solicita identificador que não corresponde a Paciente
- **THEN** o backend retorna recurso não encontrado sem revelar outros dados

### Requirement: Interface de edição segura
O sistema SHALL oferecer edição cadastral integrada à listagem de Pacientes com formulário preenchido pelo backend, ações Salvar alterações e Cancelar, validação acessível e mensagens seguras. Após sucesso, a listagem SHALL refletir o nome atualizado; após falha corrigível, os valores SHALL permanecer disponíveis para correção. Respostas técnicas e dados pessoais SHALL NOT aparecer em logs ou URLs.

#### Scenario: Salvamento confirmado
- **WHEN** a equipe salva dados válidos e o backend confirma a alteração
- **THEN** a interface informa sucesso, fecha a edição e atualiza a listagem

#### Scenario: Erro corrigível
- **WHEN** a API rejeita os dados ou a conexão falha
- **THEN** a interface informa o problema em linguagem simples, mantém o formulário para correção e não indica sucesso

#### Scenario: Cancelar edição
- **WHEN** a equipe cancela ou fecha o formulário
- **THEN** alterações não salvas são descartadas e a listagem continua disponível

### Requirement: Edição cadastral autorizada e validada
O sistema SHALL permitir que somente Administrador ou Recepcionista ativos, com sessão válida, atualizem nome, data de nascimento, CPF, telefone, celular e e-mail de um Paciente existente. O backend SHALL validar todos os campos e rejeitar campos extras, valores inválidos e CPF duplicado sem alterar o Paciente. Mensagens SHALL ser compreensíveis e não revelar dados de outro cadastro ou detalhes técnicos.

#### Scenario: Edição válida
- **WHEN** equipe autorizada envia os seis campos cadastrais válidos para Paciente existente
- **THEN** o sistema salva os dados normalizados e atualiza a data de atualização

#### Scenario: Dados inválidos ou campos extras
- **WHEN** o envio omite ou invalida campo obrigatório, inclui campo não permitido, ou informa CPF já usado por outro Paciente
- **THEN** o backend rejeita integralmente a operação sem alterar dados e retorna mensagem segura

#### Scenario: Conta ou sessão sem autorização para editar
- **WHEN** uma conta não autenticada, inativa, expirada, revogada, Paciente ou Profissional tenta editar diretamente pela API
- **THEN** o backend nega a operação sem gravar alterações

#### Scenario: Paciente inexistente
- **WHEN** equipe autorizada tenta editar identificador sem Paciente correspondente
- **THEN** o backend informa recurso não encontrado sem criar cadastro

### Requirement: Falha da API apresentada com segurança
A interface SHALL manter os valores editados após falha corrigível e SHALL apresentar mensagem compreensível conforme o erro, sem exibir resposta técnica, credenciais ou dados pessoais.

#### Scenario: Serviço indisponível durante a edição
- **WHEN** a API retorna falha de serviço ou resposta incompatível
- **THEN** a interface mantém o formulário preenchido e apresenta orientação segura sem indicar sucesso

