## Purpose

Permitir que Administrador e Recepcionista autorizados consultem e atualizem dados cadastrais de um Paciente, sem acessar informações clínicas nem alterar o histórico.

## ADDED Requirements

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

### Requirement: Falha da API apresentada com segurança
A interface SHALL manter os valores editados após falha corrigível e SHALL apresentar mensagem compreensível conforme o erro, sem exibir resposta técnica, credenciais ou dados pessoais.

#### Scenario: Serviço indisponível durante a edição
- **WHEN** a API retorna falha de serviço ou resposta incompatível
- **THEN** a interface mantém o formulário preenchido e apresenta orientação segura sem indicar sucesso
