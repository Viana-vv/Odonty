# Tarefas

## 1. Ampliar a sessão no Xano

- [x] 1.1 Ajustar no export local o padrão e o limite de `AUTH_SESSION_TTL_SECONDS` para oito horas na rota `POST /auth/login`, mantendo o mesmo prazo no registro de sessão e no token; verificar com testes unitários Python e JavaScript separados para essa rota.
- [x] 1.2 Configurar o prazo efetivo do endpoint publicado para oito horas e validar com Conta de Acesso fictícia: `expira_em` retornou aproximadamente oito horas após o login, logout respondeu 204 e a reutilização do token revogado respondeu 401.

## 2. Refletir a duração na aplicação

- [x] 2.1 Atualizar avisos de expiração e falha no logout para informar o novo limite; verificar os fluxos de sessão e expiração em `tests/test_acesso.py`.
- [x] 2.2 Confirmar que a sessão continua apenas no estado ativo do Streamlit e que perda de estado exige novo login, sem token em arquivo, URL, logs ou armazenamento do navegador; verificar os testes de acesso e inspeção de código.

## 3. Validar a change

- [x] 3.1 Executar os testes Python e JavaScript de autenticação, validar OpenSpec em modo strict e confirmar login, prazo de oito horas, logout e rejeição de token revogado no ambiente publicado.
