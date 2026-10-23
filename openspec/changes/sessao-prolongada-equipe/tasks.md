# Tarefas

## 1. Ampliar a sessão no Xano

- [x] 1.1 Ajustar no export local o padrão e o limite de `AUTH_SESSION_TTL_SECONDS` para oito horas na rota `POST /auth/login`, mantendo o mesmo prazo no registro de sessão e no token; verificar com testes unitários Python e JavaScript separados para essa rota.
- [ ] 1.2 **Pendente de execução no ambiente externo:** configurar `AUTH_SESSION_TTL_SECONDS=28800` no Xano publicado e validar com Conta de Acesso fictícia que `expira_em` retorna aproximadamente oito horas após o login e que o logout revoga a sessão. Não executar esta operação nesta etapa.

## 2. Refletir a duração na aplicação

- [x] 2.1 Atualizar avisos de expiração e falha no logout para informar o novo limite; verificar os fluxos de sessão e expiração em `tests/test_acesso.py`.
- [x] 2.2 Confirmar que a sessão continua apenas no estado ativo do Streamlit e que perda de estado exige novo login, sem token em arquivo, URL, logs ou armazenamento do navegador; verificar os testes de acesso e inspeção de código.

## 3. Validar a change

- [x] 3.1 Executar os testes locais Python e JavaScript de autenticação e `openspec validate sessao-prolongada-equipe --strict`; a confirmação de expiração e revogação no ambiente publicado permanece pendente na tarefa 1.2.
