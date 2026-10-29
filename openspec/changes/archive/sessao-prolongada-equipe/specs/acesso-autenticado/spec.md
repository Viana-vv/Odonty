# Spec Delta

## MODIFIED Requirements

### Requirement: Sessão e logout
O sistema SHALL limitar a sessão da Conta de Acesso interna a oito horas desde o login, sem renovação automática. O Xano SHALL controlar expiração e revogação. O logout SHALL limpar o estado local e revogar somente a sessão atual no Xano quando a operação remota for concluída. Sessões independentes da mesma conta SHALL permanecer válidas até sua própria expiração ou revogação.

#### Scenario: Expiração
- **WHEN** a sessão completa oito horas ou o backend informa que a autenticação perdeu a validade
- **THEN** o acesso protegido é interrompido, o estado autenticado é limpo e a interface orienta nova entrada.

#### Scenario: Saída e retorno
- **WHEN** a pessoa realiza logout e tenta retornar a uma página protegida
- **THEN** uma nova autenticação é exigida e nenhuma revogação remota é alegada sem confirmação conforme o contrato.

### Requirement: Encerramento verificável e perda de sessão
O sistema SHALL exigir novo login quando o estado da sessão do frontend for perdido e SHALL NOT persistir credenciais para restaurá-lo. A interface SHALL bloquear a apresentação protegida quando não conseguir revalidar a identidade no backend.

#### Scenario: Reutilização após logout confirmado
- **WHEN** um token de sessão revogada é reutilizado para acessar conteúdo protegido
- **THEN** o Xano rejeita o acesso mesmo que o token ainda não tenha atingido seu prazo de expiração.

#### Scenario: Falha de rede ao sair
- **WHEN** não é possível confirmar o logout remoto
- **THEN** o frontend limpa o estado local e informa que o encerramento no servidor não foi confirmado e que a sessão expira em até oito horas.

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
