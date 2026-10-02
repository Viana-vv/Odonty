## 1. Documentação de inicialização

- [x] 1.1 Atualizar a seção Executar localmente do README com instalação e inicialização no macOS e Windows, incluindo configuração de `XANO_API_BASE_URL`; verificar que cada bloco usa o caminho correto do ambiente virtual e inicia `app.py` em `http://localhost:8501`.
- [x] 1.2 Substituir a extração da credencial via DPAPI por passos seguros para obter ou solicitar uma Conta de Acesso Administrador fictícia no Xano; verificar que não são instruídos compartilhamento de senhas ou inclusão em arquivos versionados.

## 2. Revisão multiplataforma

- [x] 2.1 Revisar README, `.env.example` e arquivos de configuração para remover pressupostos de Windows relacionados a executar o app e realizar login; verificar que configurações sensíveis continuam fora do Git.
- [x] 2.2 Executar as verificações locais existentes e validar os comandos documentados nos sistemas disponíveis; registrar claramente sistemas não disponíveis para execução no ambiente de trabalho. A suíte Windows teve 198 aprovações; o teste de login que expirou na execução completa passou isoladamente. macOS não está disponível neste ambiente.
