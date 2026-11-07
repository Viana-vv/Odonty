# Recuperação de senha Specification

## Purpose

Permitir que uma pessoa recupere com segurança a senha da própria Conta de Acesso por meio de um código OTP enviado ao e-mail cadastrado.

## Requirements

### Requirement: Solicitação de recuperação
O sistema SHALL apresentar a ação “Esqueci minha senha” no login e aceitar um e-mail válido para iniciar a recuperação. A resposta SHALL ser neutra, sem confirmar se a Conta de Acesso existe.

#### Scenario: Solicitação com e-mail válido
- **WHEN** a pessoa informa um e-mail válido e solicita a recuperação
- **THEN** o sistema responde de forma neutra e, quando aplicável, envia um código OTP ao e-mail da Conta de Acesso

#### Scenario: E-mail inexistente
- **WHEN** a pessoa informa um e-mail que não está associado a uma Conta de Acesso
- **THEN** o sistema apresenta a mesma resposta neutra usada para uma solicitação existente e não revela a existência da conta

### Requirement: Validação do OTP
O sistema SHALL enviar um código OTP de seis dígitos pelo serviço de e-mail configurado, aceitar o código somente dentro do prazo de validade e limitar tentativas. O código SHALL ser armazenado somente com hash e SHALL ser invalidado após validação bem-sucedida ou expiração.

#### Scenario: OTP válido
- **WHEN** a pessoa informa o OTP correto dentro do prazo e ainda possui tentativas disponíveis
- **THEN** o sistema autoriza a etapa de definição da nova senha e não permite reutilizar o OTP

#### Scenario: OTP inválido, expirado ou excedente
- **WHEN** a pessoa informa um OTP incorreto, expirado ou excede o limite de tentativas
- **THEN** o sistema rejeita a validação, não autoriza a troca de senha e informa uma mensagem compreensível sem revelar o OTP armazenado

### Requirement: Definição de nova senha
O sistema SHALL exigir uma nova senha e sua confirmação, ambas com 12 a 128 caracteres. Após a troca bem-sucedida, SHALL invalidar a operação de recuperação, não expor a senha e redirecionar a pessoa para o login.

#### Scenario: Nova senha confirmada
- **WHEN** a pessoa informa uma nova senha válida e uma confirmação idêntica após validar o OTP
- **THEN** o sistema atualiza a credencial da Conta de Acesso, invalida a operação de recuperação e retorna à tela de login

#### Scenario: Senhas divergentes ou fora do limite
- **WHEN** a nova senha e a confirmação são diferentes ou estão fora do limite de 12 a 128 caracteres
- **THEN** o sistema rejeita a troca e orienta a correção sem alterar a Conta de Acesso
