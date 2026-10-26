## 1. Contrato

- [x] 1.1 Implementar no script local do endpoint a resposta mínima para Paciente e preservar a serialização da equipe; verificar que o código possui ramificações explícitas por perfil.
- [x] 1.2 Adaptar o parser para aceitar resposta sem nome do Paciente e sem campos de Procedimentos, mantendo o nome do Profissional; validar forma mínima e compatibilidade interna com `pytest` no arquivo de contrato.
- [x] 1.3 Ajustar o teste Python separado de `GET /consultas` para validar campos mínimos de Paciente e compatibilidade de equipe sem chamadas de rede; verificar com `pytest` no arquivo de contrato.
- [x] 1.4 Ajustar o teste JavaScript separado de `GET /consultas` para validar o mesmo contrato sem chamadas de rede; verificar com `node --test` no arquivo da rota.

## 2. Verificação

- [x] 2.1 Executar as verificações Python e JavaScript de `GET /consultas` e conferir a ausência de falhas.
- [x] 2.2 Executar `openspec validate consulta-paciente-dados-minimos --strict` e `git diff --check`; corrigir todos os problemas reportados.
- [x] 2.3 Documentar no resultado da tarefa que a correspondência e autorização no Xano real ainda exigem validação do grupo em ambiente seguro.
