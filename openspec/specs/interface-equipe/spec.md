# Interface da Equipe — Especificação

## Purpose

Define uma apresentação visual consistente e responsiva para as telas já disponíveis à equipe do Sorriso+, preservando os fluxos existentes de autenticação e cadastro.

## Requirements

### Requirement: Identidade visual das telas existentes
O sistema SHALL alinhar visualmente o login, o início da equipe e os formulários existentes de cadastro de Paciente e Profissional às referências correspondentes do projeto, incluindo o mascote fornecido sem distorção ou corte que prejudique sua identificação.

#### Scenario: Acessar o login
- **WHEN** uma pessoa abre o sistema sem sessão
- **THEN** vê o login com a identidade visual das referências e o mascote, mantendo os campos reais de e-mail e senha.

#### Scenario: Abrir início ou cadastro da equipe
- **WHEN** uma Conta de Acesso autenticada abre o início da equipe ou um formulário disponível
- **THEN** as telas mantêm paleta, tipografia, espaçamento e hierarquia visual coerentes com as referências, sem alterar campos ou ações funcionais existentes.

### Requirement: Preservação dos fluxos e permissões
O redesenho SHALL manter autenticação, mensagens, validações e autorização atuais. A interface SHALL mostrar somente ações implementadas e autorizadas para os perfis da Conta de Acesso; SHALL NOT reproduzir seletor de perfil, credenciais fixas ou botões de módulos sem funcionalidade presentes nos prints.

#### Scenario: Entrar com Conta de Acesso
- **WHEN** a equipe informa e-mail e senha cadastrados
- **THEN** o sistema utiliza o fluxo de autenticação existente sem escolher perfil ou preencher credenciais de demonstração automaticamente.

#### Scenario: Exibir ações do perfil
- **WHEN** a página inicial é exibida para Administrador, Recepcionista ou Profissional
- **THEN** cada perfil vê somente as ações já implementadas e permitidas para sua Conta de Acesso.

### Requirement: Layout responsivo e acessível
As telas SHALL permanecer legíveis e utilizáveis em computador, tablet, celular e teclado, com controles alcançáveis, foco visível e formulário sem rolagem horizontal.

#### Scenario: Reduzir a largura da tela
- **WHEN** uma tela existente é aberta em tablet ou celular
- **THEN** conteúdo, mascote, campos e ações se reorganizam sem sobreposição nem rolagem horizontal.

#### Scenario: Navegar por teclado
- **WHEN** uma pessoa percorre login ou cadastro usando teclado
- **THEN** a ordem de foco é compreensível e o foco permanece visível em cada controle.
