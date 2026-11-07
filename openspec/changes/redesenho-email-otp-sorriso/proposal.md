## Why

O e-mail OTP atual já utiliza o envio existente do Xano para o SendGrid, mas seu template visual é compacto, usa a validade fixa de dez minutos e apresenta o mascote com fundo. A mudança melhora a clareza, a identidade visual e a compatibilidade com clientes de e-mail sem alterar geração, validação, expiração ou troca de senha.

## What Changes

- Refatorar exclusivamente o HTML e o texto alternativo do e-mail OTP embutido no payload do SendGrid.
- Aplicar cabeçalho Sorriso+ verde-escuro, cartão central, ícones de segurança, código em seis blocos e rodapé informativo.
- Substituir a referência do mascote por um PNG ou WebP com transparência real, preservando o personagem original.
- Renderizar o OTP dinamicamente, preservando zeros à esquerda e permitindo seleção e cópia.
- Renderizar a validade a partir de `PASSWORD_OTP_TTL_SECONDS`, sem fixar dez minutos no template.
- Manter a parte `text/plain`, os destinatários, as credenciais por variável de ambiente, os endpoints e o fluxo atual.
- Usar tabelas HTML, CSS inline, sem JavaScript, Flexbox, Grid ou posicionamento absoluto.

Fora do escopo: alterar geração do OTP, hash, tentativas, expiração no backend, autenticação, contratos REST, banco de dados, credenciais ou configuração de produção do SendGrid/Xano.

## Capabilities

### New Capabilities

### Modified Capabilities

- `recuperacao-senha`: atualizar a apresentação do e-mail OTP, mantendo o contrato e o fluxo de recuperação existentes.

## Impact

- `backend/xano/api/sorriso_acesso/auth/recuperacao-senha_POST.xs`: somente a composição do conteúdo HTML/texto do e-mail e o valor dinâmico de validade exibido.
- `assets/mascote-sorriso-email.png` ou `.webp`: novo recorte transparente do mascote para uso em clientes de e-mail.
- Testes de contrato do endpoint e validação local do HTML; não serão feitas requisições reais ao SendGrid sem ambiente e credenciais autorizados.
- A URL pública HTTPS do mascote dependerá da publicação do arquivo no repositório ou em outro host autorizado; o template não usará caminho local nem Base64 como solução principal.
