## 1. Resumo administrativo

- [x] 1.1 Carregar, para Administrador, Consultas de hoje e cadastros ativos pelos métodos existentes; verificar chamadas com cliente simulado sem rede.
- [x] 1.2 Renderizar métricas, próxima Consulta, lista limitada e atalhos da referência; verificar dados e estado vazio em testes de interface.
- [x] 1.3 Tratar falhas, sessão expirada e acesso recusado sem exibir dados parciais ou técnicos; verificar mensagens e limpeza dos dados em testes.

## 2. Regressão e revisão

- [x] 2.1 Preservar painéis de Recepção e Profissional, atalhos e permissões; verificar testes de interface e roteamento.
- [x] 2.2 Executar os testes relevantes, `openspec validate painel-administrativo-xano --strict` e `git diff --check`; conferir que nenhum contrato novo ou chamada real de rede foi introduzido.
