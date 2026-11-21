## Purpose

Permitir que um Administrador cadastre novos tipos de Especialidade pela aplicação e os disponibilize com segurança no cadastro de Profissional.

## ADDED Requirements

### Requirement: Cadastro exclusivo de Administrador
O sistema SHALL permitir cadastrar Especialidade somente a uma Conta de Acesso ativa com perfil Administrador e sessão válida, com autorização verificada no Xano em cada envio.

#### Scenario: Administrador autorizado
- **WHEN** um Administrador ativo com sessão válida envia uma Especialidade válida
- **THEN** o sistema permite a criação

#### Scenario: Perfil sem permissão
- **WHEN** uma Conta de Acesso com perfil Recepcionista, Profissional ou Paciente chama diretamente a operação de cadastro
- **THEN** o Xano nega o acesso e não cria a Especialidade

#### Scenario: Sessão inválida
- **WHEN** o solicitante está sem autenticação, com sessão expirada ou revogada, com a conta bloqueada ou inativa, ou perdeu o perfil Administrador
- **THEN** o cadastro é rejeitado e a interface não apresenta a operação como concluída

### Requirement: Formulário administrativo de Especialidade
O sistema SHALL apresentar no painel do Administrador um formulário com o nome obrigatório da Especialidade. O nome SHALL possuir entre 2 e 120 caracteres após normalização e a nova Especialidade SHALL ser criada ativa, sem controles para alterar situação.

#### Scenario: Abrir o cadastro
- **WHEN** o Administrador seleciona a ação de cadastrar Especialidade
- **THEN** visualiza um formulário identificado como nova Especialidade, com campo de nome e ações de cadastrar e fechar

#### Scenario: Nome inválido
- **WHEN** o nome está vazio, contém somente espaços ou fica fora do limite após normalização
- **THEN** o sistema orienta a correção e não cria a Especialidade

#### Scenario: Campos não aceitos
- **WHEN** a requisição inclui identificador, situação, descrição ou qualquer campo não aceito pelo contrato
- **THEN** o Xano rejeita a requisição sem criar ou alterar Especialidades

#### Scenario: Perfil não administrativo abre o painel
- **WHEN** uma Conta de Acesso sem perfil Administrador acessa o fluxo da equipe
- **THEN** a ação e o formulário de cadastro de Especialidade não são apresentados

### Requirement: Nome normalizado e único
O sistema SHALL aparar espaços externos, reduzir sequências de espaços internos a um único espaço e comparar nomes sem diferenciar maiúsculas de minúsculas. Não SHALL existir mais de uma Especialidade com o mesmo nome normalizado, inclusive sob envios concorrentes.

#### Scenario: Cadastro concluído
- **WHEN** o Administrador envia um nome válido e inédito
- **THEN** o sistema cria uma Especialidade ativa e confirma somente identificador, nome e situação ativa

#### Scenario: Nome duplicado
- **WHEN** já existe uma Especialidade com o mesmo nome normalizado, ativa ou inativa
- **THEN** o sistema recusa o cadastro com mensagem compreensível e preserva o registro existente

#### Scenario: Envios concorrentes do mesmo nome
- **WHEN** duas requisições válidas tentam cadastrar simultaneamente o mesmo nome normalizado
- **THEN** somente uma Especialidade é criada e a outra requisição recebe conflito

### Requirement: Disponibilidade no cadastro de Profissional
Uma Especialidade criada SHALL ficar disponível na listagem de Especialidades ativas usada pelo cadastro de Profissional assim que o Xano confirmar o sucesso e a interface atualizar seus dados.

#### Scenario: Cadastrar e abrir novo Profissional
- **WHEN** o Administrador conclui o cadastro de uma Especialidade e abre ou atualiza o cadastro de Profissional
- **THEN** a nova Especialidade aparece entre as opções selecionáveis

#### Scenario: Falha ao atualizar a listagem
- **WHEN** a Especialidade foi criada, mas a atualização da listagem falha
- **THEN** a interface preserva a confirmação do cadastro, informa que as opções não puderam ser atualizadas e oferece nova tentativa de leitura sem repetir a criação

### Requirement: Resultado confiável e apresentação segura
O sistema SHALL impedir envios simultâneos pela mesma interface, SHALL NOT repetir automaticamente a criação e SHALL apresentar mensagens compreensíveis sem detalhes técnicos. O formulário SHALL seguir o padrão visual do kit Sorriso Mais e permanecer utilizável por teclado e em telas estreitas.

#### Scenario: Sucesso na interface
- **WHEN** o Xano confirma a criação
- **THEN** a interface informa o sucesso, limpa o campo e permite cadastrar outra Especialidade

#### Scenario: Falha de conexão ou resposta inválida
- **WHEN** a resposta é perdida, vazia ou incompatível com o contrato
- **THEN** a interface informa que não confirmou o cadastro e reabilita o formulário sem repetir a requisição

#### Scenario: Duplo acionamento
- **WHEN** a pessoa aciona o cadastro novamente enquanto o primeiro envio está em processamento
- **THEN** a interface mantém somente uma requisição em andamento

#### Scenario: Uso em tela estreita ou por teclado
- **WHEN** o Administrador usa o formulário em celular, tablet ou somente com teclado
- **THEN** os controles permanecem visíveis, ordenados, com foco identificável e sem exigir rolagem horizontal
