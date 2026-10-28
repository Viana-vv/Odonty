## 1. Contrato e Xano

- [x] 1.1 Adicionar teste Python por rota GET comprovando retificações e metadados retornados, sem rede real.
- [x] 1.2 Adicionar teste JavaScript do contrato GET comprovando isolamento, ordenação e ausência de conteúdo em logs.
- [x] 1.3 Alterar export GET para buscar retificações somente dos registros autorizados; validar sintaxe e escopo por teste do export.
- [x] 1.4 Revalidar/criar testes Python e JavaScript por cada POST existente (registro e retificação), cobrindo campos inválidos e autorização no export.

## 2. Interface e verificação

- [x] 2.1 Renderizar trilha append-only abaixo do conteúdo original usando os campos retornados pelo Xano; validar com AppTest.
- [x] 2.2 Executar testes Python e JavaScript dos três contratos GET/POST e AppTest do Prontuário sem chamadas de rede reais.
- [x] 2.3 Validar integração no Xano publicado com contas fictícias de Profissional, Paciente e Recepcionista, incluindo histórico e retificação; registrar bloqueio se credenciais/rotas não estiverem disponíveis. Bloqueado: não há credenciais de teste configuradas para acesso autenticado.
- [x] 2.4 Atualizar README com status real da publicação e resultado verificável; não declarar Xano validado sem integração real.
- [x] 2.5 Impedir que o GET carregue retificações para Paciente quando o Registro Clínico não estiver liberado; cobrir a autorização com testes Python e JavaScript.
