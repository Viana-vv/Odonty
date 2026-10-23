## 1. Painel conectado

- [x] 1.1 Carregar as Consultas do dia para a Recepção pelo contrato existente, com cache curto por sessão/data e atualização manual; verificar que reruns reutilizam apenas a mesma sessão e data.
- [x] 1.2 Exibir métricas, próxima Consulta, lista limitada a cinco itens e atalhos da referência sem dados clínicos ou contatos; verificar por testes da interface com dados fictícios.
- [x] 1.3 Tratar vazio, falha, 401 e 403 descartando o cache e removendo dados da resposta; verificar os estados e mensagens em testes sem rede.

## 2. Regressão e revisão

- [x] 2.1 Preservar o comportamento de Visão geral para outros perfis e validar os atalhos existentes de Agenda e Paciente; verificar testes de roteamento e da interface.
- [x] 2.2 Executar a suíte Python e JavaScript aplicável, `openspec validate painel-recepcao-xano --strict` e `git diff --check`; conferir que os testes não enviam requisições ao Xano.
- [x] 2.3 Revisar o diff, a referência visual e os arquivos alterados; conferir ausência de dados reais e credenciais antes do commit.
