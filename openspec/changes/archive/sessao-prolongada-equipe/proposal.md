# Proposta

## Por quê

A sessão da Conta de Acesso expira após uma hora, obrigando a equipe a entrar novamente durante o uso do aplicativo. A duração deve cobrir um turno de trabalho sem colocar um token fixo no código ou persistir credenciais no navegador.

## O que muda

- Ampliar para oito horas a duração máxima e padrão da sessão interna emitida pelo Xano.
- Manter a validade e a revogação sob controle do Xano e encerrar a sessão no logout.
- Manter o token somente no estado da sessão ativa do Streamlit; perda desse estado continuará exigindo novo login.
- Não criar token fixo, renovação automática nem persistência de credenciais no navegador.

## Capacidades

### Novas capacidades

Nenhuma.

### Capacidades modificadas

- `acesso-autenticado`: alterar a validade máxima da sessão interna de uma para oito horas, mantendo expiração e logout verificáveis no Xano.

## Impacto

- Xano: rota `POST /auth/login`, validação e expiração de `sessao_acesso` e configuração `AUTH_SESSION_TTL_SECONDS`.
- Streamlit: mensagens que informam o prazo de expiração da sessão.
- Testes Python e JavaScript dos contratos de autenticação, além da validação de sessão e logout.

## Fora de escopo

- Permanecer autenticado depois de fechar ou recarregar o navegador, reiniciar o Streamlit ou perder a sessão WebSocket.
- Armazenar access tokens ou senhas em arquivos, banco local, `localStorage` ou código versionado.
