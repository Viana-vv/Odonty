# Recuperação de senha por OTP

Adicionar à tela de login um link para recuperação de senha. A pessoa informa o e-mail da Conta de Acesso, recebe um código OTP por SendGrid, valida o código e define uma nova senha com confirmação. Após a troca com sucesso, retorna à tela de login.

O OTP é gerado, armazenado com hash, expirado e invalidado no Xano. A chave do SendGrid e o template são variáveis de ambiente do Xano.
