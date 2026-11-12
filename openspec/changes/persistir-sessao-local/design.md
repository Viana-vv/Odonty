## Contexto

O Streamlit lê cookies do navegador, mas o login REST executado no servidor não consegue emitir Set-Cookie para ele. O uso solicitado é apenas local.

## Decisões

Um servidor HTTP da biblioteca padrão, ligado a 127.0.0.1:8502, emite cookie host-only HttpOnly e SameSite=Strict para localhost. O inicializador abre o Streamlit em localhost:8501. HTTP local não permite exigir Secure; esta solução não é destinada a implantação remota.

O cookie contém identificador aleatório de 256 bits. Credenciais ficam em memória, nunca em URL, disco ou JavaScript. Um ticket de uso único, válido por 60 segundos, permite ativar o cookie em navegação de mesma aba e redireciona para endereço local fixo. O ticket é uma capacidade temporária e também não deve aparecer nos logs.

O prazo é o menor entre oito horas e a validade recebida do Xano. Após recarga, a credencial recuperada passa por auth/me antes de exibir conteúdo. Logout, rejeição de autorização, expiração ou reinício removem a recuperação. Falhas temporárias preservam a credencial e bloqueiam a tela até nova validação.

## Limites

Reinício do processo exige login. Uso exclusivo de localhost; portas ocupadas impedem ativação com mensagem compreensível. Não há renovação automática nem verificação remota da configuração Xano nesta mudança.
