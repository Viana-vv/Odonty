## Purpose

Manter a sessão local após recarga do navegador, com recuperação automática, revalidação no Xano e preservação da validade original.

## ADDED Requirements

### Requirement: Recuperar sessão local
O sistema SHALL oferecer recuperação após recarga em localhost usando cookie HttpOnly, SameSite=Strict e identificador opaco, mantendo credenciais somente na memória e revalidando a identidade no Xano.

#### Scenario: Login concluído
- **WHEN** o login é validado no modo local
- **THEN** a persistência é ativada automaticamente e retorna ao app sem botões ou confirmação adicional.

#### Scenario: Recarga com sessão válida
- **WHEN** o navegador possui identificador local válido após ativação
- **THEN** a credencial é recuperada e validada no Xano antes de exibir conteúdo protegido.

#### Scenario: Expiração ou logout
- **WHEN** a sessão expira, é recusada ou o usuário sai
- **THEN** o identificador deixa de recuperar credenciais.

#### Scenario: Ticket reutilizado
- **WHEN** um ticket já utilizado ou expirado é apresentado
- **THEN** o servidor recusa a ativação e não emite cookie.
