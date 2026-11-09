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

### Requirement: E-mail OTP com identidade Sorriso+ e conteúdo dinâmico
O sistema SHALL enviar o OTP existente em uma mensagem HTML compatível com clientes de e-mail, acompanhada por uma versão `text/plain` equivalente. O HTML SHALL apresentar cabeçalho Sorriso+ verde-escuro com mascote transparente, cartão branco sobre fundo cinza-claro, ícone de cadeado, título “Redefinição de senha”, instrução de uso, código de seis dígitos em blocos individuais, validade real configurada no backend, aviso de segurança com ícone de escudo e rodapé de mensagem automática.

#### Scenario: Template HTML renderizado
- **WHEN** uma solicitação válida gera um OTP e o envio ao SendGrid é preparado
- **THEN** o HTML usa tabelas e estilos inline, contém a identidade Sorriso+, o mascote com URL HTTPS pública e os textos previstos, sem JavaScript, Flexbox, Grid ou posicionamento absoluto

#### Scenario: Código e validade dinâmicos
- **WHEN** o backend prepara o e-mail com qualquer OTP de seis dígitos e uma validade configurada
- **THEN** o HTML e o texto simples exibem o mesmo OTP real, preservam zeros à esquerda, permitem seleção e cópia e informam a validade calculada a partir da configuração efetiva do backend

#### Scenario: Segurança e fluxo preservados
- **WHEN** o template visual é alterado
- **THEN** o destinatário, a geração, o armazenamento com hash, a expiração, o limite de tentativas, a validação, a troca de senha e os endpoints existentes permanecem inalterados

#### Scenario: Clientes de e-mail e telas pequenas
- **WHEN** a mensagem é aberta no Gmail, Outlook ou em um cliente móvel
- **THEN** o conteúdo permanece legível, responsivo e sem rolagem horizontal, com texto alternativo adequado para a imagem do mascote
