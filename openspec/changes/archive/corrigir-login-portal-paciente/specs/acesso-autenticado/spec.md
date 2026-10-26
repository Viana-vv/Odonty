## ADDED Requirements

### Requirement: Login independente do Paciente
O sistema MUST permitir que uma Conta de Acesso ativa com perfil `paciente` entre pelo portal independente do Paciente, com autenticação e autorização confirmadas pelo Xano. A tela MUST seguir a identidade visual Sorriso Mais, apresentar campos de e-mail e senha e MUST NOT exibir instruções que encaminhem a equipe para outro endereço. A aplicação interna SHALL permanecer exclusiva aos perfis da equipe.

#### Scenario: Paciente ativo entra no portal
- **WHEN** uma Conta de Acesso ativa com perfil `paciente` informa credenciais válidas no portal do Paciente
- **THEN** o Xano autentica a Conta de Acesso, o portal confirma a identidade e apresenta a área pessoal

#### Scenario: Credenciais ou acesso rejeitados
- **WHEN** o Xano rejeita as credenciais, a sessão ou a permissão da Conta de Acesso
- **THEN** o portal não apresenta conteúdo protegido, limpa a senha e mostra uma mensagem compreensível sem detalhes técnicos

#### Scenario: Falha de conexão durante a entrada
- **WHEN** o Xano está indisponível ou retorna resposta incompatível durante login ou confirmação de identidade
- **THEN** o portal não estabelece sessão, limpa a senha e permite tentar novamente com aviso de indisponibilidade

#### Scenario: Interface em telas estreitas
- **WHEN** o Paciente acessa o login por celular ou navega pelos campos usando teclado
- **THEN** a composição permanece legível e responsiva, com rótulos, foco visível e controles operáveis
