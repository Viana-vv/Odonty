## Context

O endpoint Xano `POST /auth/recuperacao-senha` gera o OTP, grava sua operação e envia um payload JSON diretamente ao SendGrid. O HTML atual é uma string inline, usa `%s` para o OTP, referencia `assets/mascote-sorriso.png` e fixa “10 minutos”, embora a validade venha de `PASSWORD_OTP_TTL_SECONDS`. A implementação deve permanecer no endpoint, sem criar novo serviço ou alterar os contratos.

## Goals / Non-Goals

**Goals:**

- Reestruturar o HTML como tabelas aninhadas, com CSS inline e largura adaptável.
- Manter partes HTML e `text/plain` coerentes, usando o OTP e a validade da mesma solicitação.
- Criar um recorte transparente do mascote original e referenciá-lo por HTTPS público.
- Preservar a identidade visual, a acessibilidade básica e a seleção/cópia do OTP.

**Non-Goals:**

- Alterar geração, hash, persistência, validação, expiração, tentativas ou troca de senha.
- Alterar endpoints, destinatário, autenticação do SendGrid ou variáveis secretas.
- Fazer deploy, publicar credenciais ou testar envio real sem ambiente autorizado.

## Decisions

- **Template no payload atual:** manter o conteúdo no `recuperacao-senha_POST.xs`, pois essa é a integração existente e a solicitação é exclusivamente visual. Um Dynamic Template externo do SendGrid só seria usado se já estivesse configurado; não será introduzida uma dependência nova.
- **Dinâmicos por composição do Xano:** manter a substituição do OTP no mecanismo de formatação já usado e adicionar a validade derivada de `$duracao`. Não usar o exemplo `331904` nem texto fixo de dez minutos.
- **Compatibilidade de e-mail:** usar tabelas, atributos de apresentação necessários e CSS inline; evitar recursos com suporte inconsistente. Os seis dígitos ficam em células separadas, com um trecho textual contínuo para facilitar seleção e cópia.
- **Imagem transparente:** gerar uma cópia não destrutiva do mascote original, removendo somente o fundo e preservando o personagem. O arquivo final será referenciado por uma URL HTTPS pública estável do repositório após publicação.
- **Fallback textual:** manter a parte `text/plain` sem HTML e com as mesmas informações dinâmicas da versão visual.

## Risks / Trade-offs

- [Clientes de e-mail removem parte do CSS] → usar tabelas, estilos inline e uma composição simples com largura máxima e largura fluida.
- [URL pública do mascote ainda não publicada] → manter a URL configurável/documentada e bloquear a conclusão do teste visual externo até a publicação HTTPS autorizada.
- [Conversão da validade em minutos diverge da configuração] → derivar o texto da mesma variável `$duracao` usada para `expira_em` e testar valores com zero à esquerda e validade diferente de dez minutos.
- [Tratamento automático do fundo altera o personagem] → inspecionar o PNG/WebP resultante contra o original e rejeitar qualquer mudança no desenho, cores ou detalhes.

## Migration Plan

1. Criar o ativo transparente e publicar a URL HTTPS autorizada.
2. Substituir somente a composição das partes de e-mail no endpoint Xano.
3. Executar testes estáticos dos contratos e renderização local em desktop e celular.
4. Validar no Xano/SendGrid somente com ambiente e credenciais autorizados.
5. Reverter o bloco visual e a referência do ativo se a renderização ou o envio falhar; os endpoints e a lógica do OTP não precisam de migração.
