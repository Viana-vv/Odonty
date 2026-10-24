## 1. Backend e contrato

- [x] 1.1 Criar export da tabela aditiva de vínculo entre Consultas; referências e índices únicos verificados por testes Python/JavaScript; nenhuma tabela existente foi alterada.
- [x] 1.2 Implementar export exclusivo POST /consultas/{id}/reagendamento com autorização, validação, serialização, auditoria e vínculo na mesma transação, incluindo correção autorizada de releitura em PATCH de Disponibilidade; testes de contratos e regressão estruturais passaram em Python e JavaScript, sem rede. Execução real permanece na tarefa 3.1.
- [x] 1.3 Implementar integração REST em módulo próprio usando transporte comum; payload, validações, resposta e erros verificados com HTTP simulado nos 30 testes da nova rota.

## 2. Interface

- [x] 2.1 Criar tela isolada de reagendamento com os seletores e padrão visual existentes; 20 AppTests sem rede verificaram perfis, campos obrigatórios, filtros, listas vazias, sucesso, conflito e sessão expirada.

## 3. Verificação e entrega

- [ ] 3.1 Validar compilação, autorização, conflito concorrente e rollback em grupo temporário Xano com dados fictícios e intervalo de três segundos; registrar evidências e limitações sem tocar na API de produção.
- [x] 3.2 Revisar documentação e diff; executar 43 testes de contratos Python, 49 testes de interface/transições e 7 verificações JavaScript; validar OpenSpec estrito. Entrega registrada em README.md e commit restrito à branch da Issue #64.
