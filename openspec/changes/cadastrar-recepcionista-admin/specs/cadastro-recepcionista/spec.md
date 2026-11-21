## Purpose

Permitir que um Administrador crie, pela aplicação, uma Conta de Acesso ativa com o perfil fixo de Recepcionista, sem ampliar privilégios nem expor credenciais.

## ADDED Requirements

### Requirement: Cadastro exclusivo de Administrador
O sistema SHALL permitir o cadastro de Recepcionista somente a uma Conta de Acesso ativa com perfil Administrador e sessão válida, com autorização verificada no Xano em cada envio.

#### Scenario: Administrador autorizado
- **WHEN** um Administrador ativo com sessão válida envia um cadastro válido
- **THEN** o sistema permite a criação da Conta de Acesso de Recepcionista

#### Scenario: Perfil sem permissão
- **WHEN** uma Conta de Acesso com perfil Recepcionista, Profissional ou Paciente chama diretamente a operação de cadastro
- **THEN** o Xano nega o acesso e não cria nenhuma Conta de Acesso

#### Scenario: Sessão inválida
- **WHEN** o solicitante está sem autenticação, com sessão expirada ou revogada, com a conta bloqueada ou inativa, ou perdeu o perfil Administrador
- **THEN** o cadastro é rejeitado e a interface não apresenta a operação como concluída

### Requirement: Formulário administrativo com perfil fixo
O sistema SHALL apresentar no painel do Administrador um formulário de cadastro de Recepcionista com nome, e-mail, senha inicial e confirmação da senha. O perfil SHALL ser fixado como `recepcionista` e a situação inicial SHALL ser `ativo`, sem controles para escolher outros perfis ou situações.

#### Scenario: Abrir o cadastro
- **WHEN** o Administrador seleciona a ação de cadastrar Recepcionista
- **THEN** visualiza um formulário com os campos previstos, senhas mascaradas e identificação do perfil fixo de Recepcionista

#### Scenario: Dados inválidos
- **WHEN** existe campo obrigatório vazio, nome fora do limite de 2 a 120 caracteres, e-mail inválido ou maior que 254 caracteres, senha fora do limite de 12 a 128 caracteres ou confirmação divergente
- **THEN** o sistema orienta a correção e não cria a Conta de Acesso

#### Scenario: Tentativa de escolher privilégio
- **WHEN** a requisição inclui perfil, situação, identificador ou qualquer campo não aceito pelo contrato
- **THEN** o Xano rejeita a requisição sem criar ou alterar Contas de Acesso

#### Scenario: Perfil não administrativo abre o painel
- **WHEN** uma Conta de Acesso sem perfil Administrador acessa o fluxo da equipe
- **THEN** a ação e o formulário de cadastro de Recepcionista não são apresentados

### Requirement: Criação única da Conta de Acesso de Recepcionista
O sistema SHALL normalizar o e-mail, exigir sua unicidade inclusive entre contas inativas ou bloqueadas e criar exatamente uma Conta de Acesso ativa cujo único perfil seja `recepcionista`. A criação SHALL NOT vincular a conta a um Paciente ou Profissional.

#### Scenario: Cadastro concluído
- **WHEN** o Administrador envia nome, e-mail e senha válidos e inéditos
- **THEN** o sistema cria a Conta de Acesso ativa com o único perfil Recepcionista e confirma apenas identificador, nome, e-mail, perfil e situação

#### Scenario: E-mail já cadastrado
- **WHEN** o e-mail normalizado já pertence a qualquer Conta de Acesso
- **THEN** o sistema recusa o cadastro com mensagem compreensível e preserva a conta existente

#### Scenario: Envios concorrentes do mesmo e-mail
- **WHEN** duas requisições válidas tentam cadastrar simultaneamente o mesmo e-mail normalizado
- **THEN** somente uma Conta de Acesso é criada e a outra requisição recebe conflito

### Requirement: Proteção da senha e resultado confiável
O sistema SHALL impedir envios simultâneos pela mesma interface, SHALL NOT repetir automaticamente a operação e SHALL remover senha e confirmação após o processamento ou fechamento do formulário. Senha, token e corpos sensíveis SHALL NOT aparecer em respostas, logs ou mensagens de erro.

#### Scenario: Sucesso na interface
- **WHEN** o Xano confirma a criação
- **THEN** a interface informa o sucesso, limpa os campos e permite consultar a nova Conta de Acesso sem trocar a identidade do Administrador

#### Scenario: Falha de conexão ou resposta inválida
- **WHEN** a resposta é perdida, vazia ou incompatível com o contrato
- **THEN** a interface informa que não confirmou o cadastro, limpa as senhas e reabilita o formulário sem repetir a requisição

#### Scenario: Duplo acionamento
- **WHEN** a pessoa aciona o cadastro novamente enquanto o primeiro envio está em processamento
- **THEN** a interface mantém somente uma requisição em andamento

### Requirement: Apresentação responsiva e acessível
O formulário SHALL seguir a hierarquia visual do kit Sorriso Mais e manter campos, mensagens e ações legíveis e alcançáveis por teclado em telas amplas ou estreitas.

#### Scenario: Uso em tela estreita ou por teclado
- **WHEN** o Administrador usa o formulário em celular, tablet ou somente com teclado
- **THEN** os controles permanecem visíveis, ordenados, com foco identificável e sem exigir rolagem horizontal
