## 1. Ativo visual

- [x] 1.1 Remover somente o fundo do mascote original e gerar PNG ou WebP com transparência real; verificar dimensões, canal alfa e comparação visual com `assets/mascote-sorriso.png`.
- [x] 1.2 Publicar o ativo em uma URL HTTPS pública autorizada e verificar que a URL responde sem autenticação e que a imagem não contém fundo branco.

## 2. Template Xano/SendGrid

- [x] 2.1 Substituir somente a composição HTML do e-mail em `recuperacao-senha_POST.xs`, usando tabelas, CSS inline, cabeçalho, cartão, ícones, seis blocos do OTP, aviso de segurança e rodapé; verificar ausência de JavaScript, Flexbox, Grid e posicionamento absoluto.
- [x] 2.2 Manter a parte `text/plain` e fazê-la usar o mesmo OTP e a mesma validade dinâmica da versão HTML; verificar preservação de zeros à esquerda e ausência de `331904` fixo.
- [x] 2.3 Derivar o texto de validade de `PASSWORD_OTP_TTL_SECONDS`/`$duracao` e verificar o template com valores diferentes de dez minutos.
- [x] 2.4 Publicar o ativo e confirmar a referência do mascote em uma URL HTTPS pública; depois verificar texto alternativo, seleção/cópia do OTP e legibilidade em largura móvel.

## 3. Verificação

- [x] 3.1 Executar os testes unitários Python e JavaScript dos contratos de recuperação sem requisições reais; verificar que geração, validação, expiração, tentativas, troca de senha, destinatário e endpoints não foram alterados.
- [x] 3.2 Validar o HTML e CSS e renderizar a mensagem em desktop e celular com OTP iniciado por zero; verificar que não há rolagem horizontal e que os seis dígitos aparecem na ordem correta.
- [ ] 3.3 Testar o envio real pelo Xano/SendGrid somente em ambiente e com credenciais autorizados; registrar eventual configuração manual necessária para publicação da imagem ou template.

## Evidências da execução

- Issue: https://github.com/Viana-vv/Odonty/issues/135.
- Ativo publicado em URL HTTPS fixa: https://raw.githubusercontent.com/Viana-vv/Odonty/1997d30443ffe2839bd407e2a5ae733d876ee83b/assets/mascote-sorriso-email.png. Resposta HTTP 200 sem autenticação; conteúdo idêntico ao PNG local e canal alfa de 0 a 255.
- Template publicado no endpoint existente `POST /auth/recuperacao-senha` do grupo Sorriso Acesso; leitura posterior confirmou o novo ativo e a validade dinâmica. Somente o bloco de composição do e-mail foi substituído na versão remota.
- Python: 13 testes aprovados, incluindo renderização em 320, 390, 600 e 1440 px, imagem carregada, seis dígitos na ordem correta e seleção do código contínuo `012304`.
- JavaScript: 3 testes de contrato aprovados, sem requisições reais ao SendGrid.
- A prévia do Xano indicou a atualização de apenas um endpoint. Não foram publicadas tabelas nem variáveis de ambiente.
- Envio real e inspeção em Gmail/Outlook não executados: não há destinatário de teste indicado para envio. A publicação da imagem e do template não depende de configuração manual adicional.
