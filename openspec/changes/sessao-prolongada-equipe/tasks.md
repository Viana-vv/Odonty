# Tarefas

## 1. Ampliar a sessão no Xano

- [ ] 1.1 Ajustar o padrão e o limite de `AUTH_SESSION_TTL_SECONDS` para oito horas na rota `POST /auth/login`, mantendo o mesmo prazo no registro de sessão e no token; verificar com testes unitários Python e JavaScript separados para essa rota.
- [ ] 1.2 Atualizar a configuração do ambiente Xano para `28800` segundos e validar com Conta de Acesso fictícia que `expira_em` retorna aproximadamente oito horas após o login e que o logout revoga a sessão.

## 2. Refletir a duração na aplicação

- [ ] 2.1 Atualizar avisos de expiração e falha no logout para informar o novo limite; verificar os fluxos de sessão e expiração em `tests/test_acesso.py`.
- [ ] 2.2 Confirmar que a sessão continua apenas no estado ativo do Streamlit e que perda de estado exige novo login, sem token em arquivo, URL, logs ou armazenamento do navegador; verificar os testes de acesso e inspeção de código.

## 3. Validar a change

- [ ] 3.1 Executar os testes Python e JavaScript de autenticação e `openspec validate sessao-prolongada-equipe --strict`; confirmar login, expiração, logout, conta inativa e sessão revogada.
