## Decisão

O OTP permanece numérico e com seis caracteres, conforme `sorrisomais.recuperacao.validar_otp` e o endpoint Xano de validação. O Streamlit renderiza seis `text_input` com chaves independentes; o valor enviado continua sendo a concatenação desses estados.

Um script pequeno no DOM da etapa OTP configura `inputmode` numérico, filtra caracteres, avança o foco, trata backspace e distribui colagens. Os estilos usam a paleta existente (`--verde`, `--linha`) e media queries para reduzir os campos e o espaçamento em telas estreitas.

Não haverá mudança no endpoint, na geração, no contrato de envio pelo SendGrid ou nas regras de expiração/tentativas do Xano.

O payload do SendGrid passará a incluir partes `text/plain` e `text/html`. A versão HTML usa a imagem pública da marca armazenada no repositório e CSS inline compatível com clientes de e-mail; o contrato de entrada e a resposta do endpoint permanecem inalterados.
