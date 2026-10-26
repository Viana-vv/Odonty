## Why

O endpoint `GET /consultas` atualmente serializa nomes de Procedimentos na resposta que também pode ser consumida pelo perfil Paciente. A Issue #90 restringe a visualização do Paciente aos dados administrativos mínimos aprovados, reduzindo a exposição e mantendo a resposta usada pela equipe compatível.

## What Changes

- Para o perfil Paciente, retornar somente identificadores da Consulta, Paciente e Profissional, data e hora de início e fim, situação e nome do Profissional necessário à visualização.
- Omitir da resposta ao Paciente nomes e identificadores de Procedimentos, bem como campos internos e demais dados da equipe.
- Manter o formato de resposta atual para Profissional, Administrador e Recepcionista.
- Cobrir os dois formatos do contrato com testes unitários Python e JavaScript sem chamadas reais à rede.
- Registrar que a validação de autorização e resposta no Xano real depende de uma revisão segura do grupo.

Fora de escopo: mudanças na navegação, no portal/tela do Paciente ou nos filtros e regras de consulta já existentes.

## Capabilities

### New Capabilities
- `consultas`: Contrato de `GET /consultas` com dados mínimos específicos por perfil.

### Modified Capabilities

## Impact

- API Xano: `backend/xano/api/sorriso_acesso/consultas_GET.xs`.
- Testes unitários do contrato `GET /consultas` em Python e JavaScript.
- Nenhuma alteração de modelo de dados, frontend ou dependência.
- A implementação versionada do endpoint requer validação no Xano real em grupo seguro antes de ser considerada efetiva em produção.
