## ADDED Requirements

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
