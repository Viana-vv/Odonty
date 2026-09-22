## Purpose

Permitir que uma Conta de Acesso interna entre no Sorriso+ com identidade e permissões verificadas no Xano, sessão válida e logout.

Rascunho para revisão. E-mail/senha e conteúdo da página inicial já aprovados. A proposta de contrato, matriz e política de uma hora descrita no design ainda aguarda aprovação; estes requisitos não comprovam implementação.

## ADDED Requirements

### Requirement: Interface acessível Sorriso+
O sistema SHALL apresentar identidade Sorriso+, tons verdes, textos em português brasileiro, rótulos claros, campos obrigatórios “E-mail” e “Senha” e botão “Entrar”. A senha SHALL ser mascarada. A imagem fornecida SHALL orientar a ilustração sem reproduzir os textos genéricos da marca.

#### Scenario: Dispositivos e teclado
- **WHEN** a pessoa utiliza computador, tablet ou celular e navega pelo teclado
- **THEN** o formulário permanece legível, sem sobreposição, com controles alcançáveis e foco visível.

#### Scenario: Campos inválidos
- **WHEN** existem campos ausentes ou inválidos conforme o contrato aprovado
- **THEN** a interface orienta a correção e não estabelece sessão.

#### Scenario: Envio em andamento
- **WHEN** uma autenticação está sendo processada
- **THEN** a interface informa o andamento e impede submissões duplicadas até sua conclusão.

### Requirement: Autenticação real
O sistema SHALL autenticar por e-mail e senha pelo Xano e obter identidade, situação e perfis da Conta de Acesso pelo backend. Contas bloqueadas ou inativas SHALL NOT entrar. Simulações e credenciais demonstrativas SHALL NOT conceder acesso na aplicação final.

#### Scenario: Entrada válida
- **WHEN** o Xano autentica uma conta ativa e autoriza seu acesso inicial
- **THEN** a aplicação estabelece sessão conforme o contrato e apresenta somente o nome e o perfil da Conta de Acesso retornados pelo backend e o botão “Sair”, sem dados clínicos.

#### Scenario: Entrada rejeitada
- **WHEN** as credenciais são incorretas ou a conta está inativa ou bloqueada
- **THEN** o acesso é negado com mensagem compreensível e sem detalhes sensíveis.

#### Scenario: Falha de integração
- **WHEN** ocorre falha de rede, timeout, erro de serviço, resposta vazia ou incompatível com o contrato
- **THEN** não é concedido novo acesso, o estado de envio termina e a interface permite tentar novamente com mensagem de indisponibilidade.

### Requirement: Autorização no Xano
O sistema SHALL validar autenticação e autorização no backend em toda operação protegida. Uma seleção ou alteração de perfil na interface SHALL NOT conceder permissões. Esta change abrange Administrador, Recepcionista e Profissional, exibido como Dentista; não implementa acesso de Paciente.

#### Scenario: Acesso sem autenticação
- **WHEN** alguém abre uma página protegida ou chama uma operação sem credencial válida
- **THEN** a interface exige autenticação sem apresentar conteúdo protegido e o Xano rejeita a operação.

#### Scenario: Falta de permissão
- **WHEN** uma conta autenticada tenta uma operação não autorizada pela matriz aprovada
- **THEN** o Xano rejeita a operação e a interface informa falta de permissão sem expor dados protegidos.

#### Scenario: Perfil adulterado
- **WHEN** alguém modifica o estado local para aparentar outro perfil
- **THEN** as permissões efetivas continuam sendo aquelas validadas pelo Xano.

### Requirement: Sessão e logout
O sistema SHALL limitar a sessão a uma hora desde o login, sem renovação automática, conforme política proposta. O logout SHALL limpar o estado local e revogar somente a sessão atual no Xano quando a operação remota for concluída. Sessões independentes da mesma conta SHALL permanecer válidas até sua própria expiração ou revogação.

#### Scenario: Expiração
- **WHEN** a sessão expira ou o backend informa que a autenticação perdeu a validade
- **THEN** o acesso protegido é interrompido, o estado autenticado é limpo e a interface orienta nova entrada.

#### Scenario: Saída e retorno
- **WHEN** a pessoa realiza logout e tenta retornar a uma página protegida
- **THEN** uma nova autenticação é exigida e nenhuma revogação remota é alegada sem confirmação conforme o contrato.

### Requirement: Proteção de credenciais
O sistema SHALL NOT expor senhas, tokens e segredos em código versionado, URLs, logs ou mensagens de erro. A senha SHALL NOT ser persistida após o processamento da autenticação.

#### Scenario: Erro com dados sensíveis
- **WHEN** uma resposta técnica contém informações sensíveis
- **THEN** a interface e os registros de diagnóstico não reproduzem essas informações.

### Requirement: Fluxos auxiliares reais
O sistema SHALL apresentar cadastro ou recuperação de senha somente após definição, aprovação e suporte real no backend.

#### Scenario: Fluxos não definidos
- **WHEN** cadastro ou recuperação não estão definidos e implementados
- **THEN** a tela não oferece ações que simulem esses processos.


### Requirement: Acesso inicial limitado à própria identificação
O sistema SHALL permitir aos perfis internos Administrador, Recepcionista e Profissional consultar somente o próprio nome e perfis nesta página. A conta SHALL estar ativa. Contas somente com perfil Paciente ou sem perfil interno reconhecido SHALL NOT acessar a aplicação interna. Esta change SHALL NOT conceder operações clínicas ou de administração de outras contas.

#### Scenario: Vários perfis internos
- **WHEN** a conta possui mais de um perfil interno autorizado
- **THEN** a página comum apresenta os perfis internos retornados pelo backend, sem exigir escolha ou conceder privilégios por seleção.

#### Scenario: Conta fora do recorte interno
- **WHEN** uma conta possui somente perfil Paciente ou nenhum perfil interno reconhecido
- **THEN** o backend nega acesso à página inicial e a interface não apresenta conteúdo protegido.

#### Scenario: Identidade de outra conta
- **WHEN** alguém tenta fornecer um identificador para consultar outra conta pela operação de identidade
- **THEN** a operação não retorna dados dessa outra conta.

### Requirement: Encerramento verificável e perda de sessão
O sistema SHALL exigir novo login quando o estado da sessão do frontend for perdido e SHALL NOT persistir credenciais para restaurá-lo. A interface SHALL bloquear a apresentação protegida quando não conseguir revalidar a identidade no backend.

#### Scenario: Reutilização após logout confirmado
- **WHEN** um token de sessão revogada é reutilizado para acessar conteúdo protegido
- **THEN** o Xano rejeita o acesso mesmo que o token ainda não tenha atingido seu prazo de expiração.

#### Scenario: Falha de rede ao sair
- **WHEN** não é possível confirmar o logout remoto
- **THEN** o frontend limpa o estado local e informa que o encerramento no servidor não foi confirmado e que a sessão expira em até uma hora.

#### Scenario: Logout repetido
- **WHEN** o logout é repetido com token ainda válido de sessão já revogada
- **THEN** a operação confirma o encerramento sem criar efeitos adicionais.

#### Scenario: Perda de acesso antes de sair
- **WHEN** a conta perdeu perfil interno ou foi inativada, mas possui token válido de sua sessão
- **THEN** o backend permite revogar essa sessão sem conceder acesso ao conteúdo protegido.

#### Scenario: Recarga com perda de estado
- **WHEN** uma recarga, nova aba ou reinício resulta em nova sessão do frontend
- **THEN** a aplicação exige nova autenticação, sem recuperar credenciais do navegador.

#### Scenario: Revalidação indisponível
- **WHEN** a consulta de identidade falha por indisponibilidade ou resposta inválida
- **THEN** a interface limpa o estado autenticado e informa indisponibilidade sem apresentar identidade em cache.
