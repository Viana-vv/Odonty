# Design

## Contexto

Consulte `proposal.md` para a motivação e `specs/acesso-autenticado/spec.md` para os comportamentos. Hoje, o Xano cria uma sessão por login com `AUTH_SESSION_TTL_SECONDS` padrão de 3600 segundos e limite máximo de uma hora. O Streamlit conserva o access token apenas no estado da conexão atual.

## Objetivos / Fora de escopo

**Objetivos:**
- Fazer o Xano emitir sessões internas válidas por até oito horas e usar o mesmo prazo no registro `sessao_acesso` e no token.
- Manter revogação, expiração, situação da Conta de Acesso e autorização no Xano.
- Informar o novo limite nos avisos de sessão do Streamlit.

**Fora de escopo:**
- Recuperar sessão depois de recarga, fechamento do navegador, nova conexão WebSocket ou reinício do Streamlit.
- Armazenar token em arquivo, cookie acessível ao cliente, `localStorage` ou código.
- Criar refresh token ou prolongar a sessão automaticamente.

## Decisões

- Usar `AUTH_SESSION_TTL_SECONDS` no Xano com padrão `28800` e validação de máximo `28800`, em vez de fixar o token no frontend. A configuração da instância Xano deve receber o mesmo valor para que o limite efetivo seja oito horas.
- Aplicar o prazo tanto a `sessao_acesso.expira_em` quanto à expiração do auth token. `auth/me` continua retornando o prazo de backend, e toda rota protegida segue validando a sessão no Xano.
- Conservar o access token somente no `st.session_state` durante a conexão ativa. Essa escolha mantém o requisito atual de novo login quando o estado WebSocket é perdido e evita persistência de credenciais no navegador.
- Atualizar mensagens de expiração e logout sem confirmação para refletir o prazo de até oito horas. O logout confirmado continua revogando a sessão atual imediatamente.
- Manter o limite configurável para permitir que a clínica reduza o prazo em outro ambiente; o backend rejeita valores fora do intervalo permitido.

## Riscos / compensações

- Um token comprometido pode ser usado por mais tempo → manter o token fora de logs e armazenamento do navegador, validar situação e revogação em cada operação protegida e permitir logout remoto.
- A variável Xano pode permanecer em 3600 segundos → publicar a rota e ajustar `AUTH_SESSION_TTL_SECONDS` na configuração do ambiente antes de validar o prazo real.
- Uma recarga ainda exige login → comunicar esse limite; persistência entre conexões requer outra solução de sessão segura e não faz parte desta change.

## Plano de migração

Publicar o endpoint `POST /auth/login` com o limite de oito horas e atualizar a variável Xano `AUTH_SESSION_TTL_SECONDS` para `28800`. As sessões já emitidas mantêm o prazo original; novos logins recebem o novo prazo. Para reverter, restaurar o limite anterior de `3600` e publicar a rota compatível. Não há migração de dados.
