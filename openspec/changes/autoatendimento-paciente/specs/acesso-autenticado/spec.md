## MODIFIED Requirements

### Requirement: Acesso inicial limitado à própria identificação
O sistema SHALL permitir aos perfis internos Administrador, Recepcionista e Profissional consultar o próprio nome e perfis. Administrador SHALL acessar Cadastrar profissional conforme cadastro-profissional; Administrador e Recepcionista SHALL acessar Cadastrar paciente conforme cadastro-paciente. A conta SHALL estar ativa. Contas somente com perfil Paciente ou sem perfil interno reconhecido SHALL NOT acessar a aplicação interna; o Paciente SHALL usar o entrypoint independente especificado em `autoatendimento-paciente`, com identidade e escopo confirmados pelo Xano. O acesso interno SHALL NOT conceder operações clínicas; a criação vinculada de Conta de Acesso de Profissional SHALL ser exclusiva de Administrador.

#### Scenario: Vários perfis internos
- **WHEN** a conta possui mais de um perfil interno autorizado
- **THEN** a página apresenta os perfis internos retornados pelo backend e as ações autorizadas pela presença de administrador ou recepcionista, sem exigir escolha nem conceder privilégios por seleção local

#### Scenario: Conta fora do recorte interno
- **WHEN** uma conta possui somente perfil Paciente ou nenhum perfil interno reconhecido
- **THEN** o frontend não exibe a área da equipe e o Xano nega operações internas não autorizadas

#### Scenario: Identidade de outra conta
- **WHEN** alguém tenta fornecer um identificador para consultar outra conta pela operação de identidade
- **THEN** a operação não retorna dados dessa outra conta

#### Scenario: Equipe separada de Paciente
- **WHEN** uma pessoa abre o login da equipe
- **THEN** encontra acesso exclusivo aos perfis internos, sem cadastro público ou login de Paciente nessa superfície; o cadastro administrativo de Paciente exige autenticação da equipe

#### Scenario: Recepcionista sem gestão de profissionais
- **WHEN** uma conta apenas de Recepcionista acessa sua página
- **THEN** encontra Cadastrar paciente e Sair, sem ação de cadastro de Profissional

#### Scenario: Conta Paciente no autoatendimento
- **WHEN** uma Conta de Acesso ativa com perfil Paciente autentica no entrypoint independente
- **THEN** a Conta de Acesso só consulta os próprios dados liberados conforme os contratos e requisitos de `autoatendimento-paciente`
