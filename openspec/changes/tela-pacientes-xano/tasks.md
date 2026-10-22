## 1. Tela conectada

- [x] 1.1 Criar módulo isolado de listagem que obtenha opções pela rota autorizada existente e apresente somente ID e nome; verificado por teste sem rede que o cliente existente é chamado com a sessão e apenas `pacientes` é renderizado.
- [x] 1.2 Implementar busca por nome e estados de carregamento, falha e lista vazia com a referência visual aprovada; verificado por testes da interface sem rede.

## 2. Verificação e revisão

- [x] 2.1 Criar testes de UI para sucesso, filtro, vazio, erro e autorização recusada usando cliente simulado; verificado com 8 testes próprios e sem requisições reais.
- [x] 2.2 Executar testes pertinentes, validar OpenSpec e revisar diff para confirmar escopo isolado, privacidade e compatibilidade visual; verificado com pytest, Node, `openspec validate --strict` e revisão do diff.
