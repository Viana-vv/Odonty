# Recuperação de senha

## Solicitação

O sistema SHALL apresentar “Esqueci minha senha” no login e aceitar um e-mail válido. A resposta SHALL ser neutra, sem confirmar se a Conta de Acesso existe.

## OTP

O sistema SHALL enviar um código de seis dígitos pelo SendGrid, aceitar o código somente dentro do prazo e limitar tentativas. O código SHALL ser armazenado somente com hash e SHALL ser invalidado após validação e uso.

## Nova senha

O sistema SHALL exigir nova senha e confirmação entre 12 e 128 caracteres. Após sucesso, SHALL invalidar a operação e redirecionar para o login.
