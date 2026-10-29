## 1. Backend e contrato

- [x] 1.1 Criar export aditivo para vínculo entre Consultas, índices únicos e referências; preservar os dados existentes.
- [x] 1.2 Implementar POST `/consultas/{id}/reagendamento` com autorização, validação, auditoria e vínculo na mesma transação; alinhar o PATCH de Disponibilidade à trava `agenda_controle` e reler o estado antes da gravação.
- [x] 1.3 Implementar cliente REST dedicado com payload, validações, respostas e erros verificados por HTTP simulado.

## 2. Interface

- [x] 2.1 Criar tela isolada de reagendamento no padrão visual Sorriso Mais. Vinte AppTests verificaram seletores, filtros, estados, perfis, sucesso, conflito, falha e sessão expirada.

## 3. Verificação e entrega

- [x] 3.1 Validar exports em grupo Xano temporário. Em 25/10/2026, o dry-run confirmou somente criações; a execução passou com 74 requisições e intervalo mínimo medido de 3,188 s. Compilaram 13 tabelas, uma função e sete rotas. Os cenários cobriram autenticação, autorização, validação, sucesso de Administrador e Recepcionista, vínculos e relações preservados, conflito, rollback e quatro disputas concorrentes (mesma Consulta, destino, Paciente e edição do destino). Cada disputa sobreposta terminou em 201/409. A limpeza confirmou remoção do grupo, 13 tabelas e função.
- [x] 3.2 Executar 56 testes Python, cinco verificações JavaScript, `openspec validate reagendar-consulta --strict` e `git diff --check`; todos passaram.

A primeira inspeção read-only de 24/10/2026 está preservada em `verificacao-xano-2026-10-24.md`. Os conflitos de trava nela identificados foram corrigidos e exercitados no grupo temporário em 25/10. Nenhuma API de produção foi chamada ou alterada.
