## 1. Reconciliação documental

- [x] 1.1 Consultar ajuda do OpenSpec CLI e confirmar que não há comando suportado para restaurar/emendar changes arquivadas.
- [x] 1.2 Recuperar para esta change ativa a spec de cadastro profissional a partir do delta original arquivado, sem acrescentar requisitos.
- [x] 1.3 Registrar evidência e limites para cada tarefa histórica aberta da auditoria.
- [x] 1.4 Validar esta change com `openspec validate reconciliar-artefatos-arquivados-issue-101 --strict` e revisar o diff.

## 2. Pendências factuais preservadas

- [ ] 2.1 Executar no Xano publicado a matriz 401/403 de `cadastro-profissional-admin` (tarefa histórica 2.2a); requer acesso ao ambiente e conta fictícia adequada.
- [ ] 2.2 Executar no Xano publicado cenários 201/400/409, rollback e concorrência (tarefa histórica 2.3a); requer acesso ao ambiente.
- [ ] 2.3 Inspecionar logs reais do Xano para confirmar ausência de senha, hash e token (tarefa histórica 2.4a); requer acesso aos logs.
- [ ] 2.4 Registrar decisão do grupo sobre a lacuna processual da Issue #3/retomada sem PR, caso ainda seja necessária à política de entrega; o registro histórico diz para aguardar novo pedido.
