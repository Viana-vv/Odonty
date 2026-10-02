## MODIFIED Requirements

### Requirement: Autenticação real
O sistema SHALL autenticar por e-mail e senha pelo Xano e obter identidade, situação e perfis da Conta de Acesso pelo backend. Contas bloqueadas ou inativas SHALL NOT entrar. Simulações e credenciais demonstrativas SHALL NOT conceder acesso na aplicação final.

#### Scenario: Entrada válida
- **WHEN** o Xano autentica uma conta ativa e autoriza seu acesso inicial
- **THEN** a aplicação estabelece sessão conforme o contrato e apresenta nome, perfil e Sair; para Administrador, apresenta também a página administrativa com Cadastrar profissional, sem dados clínicos.

#### Scenario: Entrada rejeitada
- **WHEN** as credenciais são incorretas ou a conta está inativa ou bloqueada
- **THEN** o acesso é negado com mensagem compreensível e sem detalhes sensíveis.

#### Scenario: Falha de integração
- **WHEN** ocorre falha de rede, timeout, erro de serviço, resposta vazia ou incompatível com o contrato
- **THEN** não é concedido novo acesso, o estado de envio termina e a interface permite tentar novamente com mensagem de indisponibilidade.

### Requirement: Acesso inicial limitado à própria identificação
O sistema SHALL permitir aos perfis internos Administrador, Recepcionista e Profissional consultar o próprio nome e perfis; Administrador também SHALL acessar sua página com Cadastrar profissional, conforme a capacidade cadastro-profissional. A conta SHALL estar ativa. Contas somente com perfil Paciente ou sem perfil interno reconhecido SHALL NOT acessar a aplicação interna. O acesso inicial SHALL NOT conceder operações clínicas; a criação vinculada de Conta de Acesso de Profissional SHALL ser exclusiva de Administrador pela capacidade cadastro-profissional.

#### Scenario: Vários perfis internos
- **WHEN** a conta possui mais de um perfil interno autorizado
- **THEN** a página apresenta os perfis internos retornados pelo backend; se incluem administrador, oferece a página administrativa, sem exigir escolha nem conceder privilégios por seleção local.

#### Scenario: Conta fora do recorte interno
- **WHEN** uma conta possui somente perfil Paciente ou nenhum perfil interno reconhecido
- **THEN** o backend nega acesso à página inicial e a interface não apresenta conteúdo protegido.

#### Scenario: Identidade de outra conta
- **WHEN** alguém tenta fornecer um identificador para consultar outra conta pela operação de identidade
- **THEN** a operação não retorna dados dessa outra conta.

#### Scenario: Equipe separada de Paciente
- **WHEN** uma pessoa abre o login da equipe
- **THEN** encontra acesso exclusivo aos perfis internos, sem cadastro ou login de Paciente nesta superfície.
