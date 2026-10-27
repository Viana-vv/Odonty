## Context

O CLI OpenSpec 1.10.0 oferece `new change`, `validate` e `archive`, mas não oferece comando para restaurar ou emendar uma change dentro de `changes/archive`. A retomada `2026-10-02-retomada-cadastro-profissional-admin` tem proposal/design/tasks e nenhum diretório `specs/`. Sua proposal registra expressamente “Nenhuma” capability nova ou modificada e limita o trabalho a corrigir uma divergência de interface e documentar testes locais. A change de origem `cadastro-profissional-admin` contém as specs de `cadastro-profissional` e `acesso-autenticado` que serviram como contrato para a retomada.

## Goals / Non-Goals

**Goals:** disponibilizar em uma change ativa um registro verificável da spec fonte ausente na retomada; preservar a distinção entre evidência local e validação remota; reconciliar somente tarefas que tenham evidência documental.

**Non-Goals:** mudar comportamento do produto, sincronizar specs principais, alterar manualmente qualquer diretório arquivado, reabrir uma implementação funcional ou realizar operações no GitHub/Xano.

## Decisions

1. `specs/cadastro-profissional/spec.md` registra o requisito modificado de formulário cuja correção a retomada relata: o botão de retorno passa a exibir “Voltar”, conforme requisito da spec original. A evidência de código/teste está em `tests/test_profissionais.py` (assert de botão “Voltar” e teste do fluxo de retorno). O texto do requisito e seus demais cenários foram recuperados da spec arquivada de origem; nenhum requisito de autenticação foi inferido ou incluído.
2. O registro é feito nesta change ativa porque não há comando CLI para restaurar a change arquivada; não se altera o histórico arquivado manualmente nem se afirma que esta ação retroage sua data ou conteúdo.
3. Tarefas de verificação Xano 2.2a, 2.3a e 2.4a continuam abertas: a própria documentação da retomada exclui chamadas remotas, e testes/dumps locais não provam resultados ou logs de produção.
4. As tarefas processuais 1.2 e 4.4 do cadastro de Paciente continuam abertas. O texto registra ausência de Issue própria e de revisão ao PR #5; os PRs #5/#6 comprovam integração de código, mas não satisfazem retrospectivamente Issue ou revisão.
5. As tarefas da retomada para auditoria local, testes, correção do rótulo e README permanecem [x] conforme evidência anotada no próprio tasks.md. A tarefa 3.2 registra que PR não deve ser aberto até nova solicitação; a integração/entrega externa não foi reivindicada como concluída.

## Risks / Trade-offs

- A spec recuperada nesta change não altera o arquivo da retomada no archive; o defeito histórico fica rastreável, mas permanece fisicamente sem spec no diretório antigo.
- Não alterar tarefas arquivadas evita reescrever registros históricos sem CLI suportado. Esta change fornece o inventário e o estado factual para revisão do grupo.

## Migration Plan

Nenhuma migração de produto. Validar esta change com `openspec validate reconciliar-artefatos-arquivados-issue-101 --strict`; revisar a proveniência dos requisitos e manter pendências explícitas.

## Inventário de specs arquivadas

Foram encontradas 39 pastas em `openspec/changes/archive`. 38 possuem ao menos um arquivo `specs/<capacidade>/spec.md`; a única sem spec é `2026-10-02-retomada-cadastro-profissional-admin`. Todas as 39 possuem `proposal.md`, `design.md` e `tasks.md`. As 38 com spec são:

`2026-09-25-login-streamlit-xano`, `2026-09-28-redesenho-telas-prontas`, `2026-09-30-cadastro-paciente-equipe`, `2026-10-01-compatibilidade-macos-windows`, `2026-10-01-recriacao-layout-sorriso-mais`, `agenda-consultas-registros-clinicos-api`, `ajuste-responsividade-painel-profissional-86`, `autoatendimento-paciente`, `cache-consultas-agenda-xano`, `cadastro-profissional-admin`, `cadastro-profissional-refino`, `consulta-paciente-dados-minimos`, `consultas-paciente`, `contas-acesso-65`, `corrigir-edicao-paciente-menu-fixo`, `corrigir-login-portal-paciente`, `editar-paciente-xano`, `gestao-disponibilidades-site`, `gestao-exames`, `gestao-horarios`, `gestao-profissionais`, `nova-consulta-refino`, `nova-evolucao-clinica`, `novos-cadastros-visuais`, `painel-administrativo-xano`, `painel-dentista-xano`, `painel-profissional-refino`, `painel-recepcao-xano`, `procedimentos-realizados`, `reagendar-consulta`, `sessao-prolongada-equipe`, `smoke-contratos-xano`, `tela-agenda-xano`, `tela-nova-consulta-xano`, `tela-pacientes-xano`, `tela-procedimentos-xano`, `tela-profissionais-xano` e `tela-prontuario-xano`.

O inventário de tarefas mostra 2 changes com checkboxes abertas: `2026-09-30-cadastro-paciente-equipe` (1.2 e 4.4) e `cadastro-profissional-admin` (2.2a, 2.3a e 2.4a). Os diretórios de `2026-10-02-retomada-cadastro-profissional-admin` registram as tarefas existentes como concluídas, com evidências locais, e não contêm pendências marcadas. As cinco tarefas abertas permanecem abertas porque tratam de processo externo não retroativo ou de validações remotas sem evidência disponível.

## Mapeamento por change e delta spec

- 2026-09-25-login-streamlit-xano: specs/acesso-autenticado/spec.md
- 2026-09-28-redesenho-telas-prontas: specs/interface-equipe/spec.md
- 2026-09-30-cadastro-paciente-equipe: specs/acesso-autenticado/spec.md, specs/cadastro-paciente/spec.md
- 2026-10-01-compatibilidade-macos-windows: specs/execucao-local-multiplataforma/spec.md
- 2026-10-01-recriacao-layout-sorriso-mais: specs/interface-equipe/spec.md
- 2026-10-02-retomada-cadastro-profissional-admin: **ausente**
- agenda-consultas-registros-clinicos-api: specs/agenda-consultas/spec.md, specs/registro-clinico/spec.md
- ajuste-responsividade-painel-profissional-86: specs/interface-equipe/spec.md
- autoatendimento-paciente: specs/acesso-autenticado/spec.md, specs/autoatendimento-paciente/spec.md
- cache-consultas-agenda-xano: specs/interface-equipe/spec.md
- cadastro-profissional-admin: specs/acesso-autenticado/spec.md, specs/cadastro-profissional/spec.md
- cadastro-profissional-refino: specs/cadastro-profissional/spec.md
- consulta-paciente-dados-minimos: specs/consultas/spec.md
- consultas-paciente: specs/consultas-do-paciente/spec.md
- contas-acesso-65: specs/consulta-contas-acesso/spec.md
- corrigir-edicao-paciente-menu-fixo: specs/edicao-paciente/spec.md, specs/interface-equipe/spec.md
- corrigir-login-portal-paciente: specs/acesso-autenticado/spec.md
- editar-paciente-xano: specs/edicao-paciente/spec.md
- gestao-disponibilidades-site: specs/gestao-disponibilidades/spec.md
- gestao-exames: specs/exames/spec.md
- gestao-horarios: specs/interface-equipe/spec.md
- gestao-profissionais: specs/gestao-profissionais/spec.md
- nova-consulta-refino: specs/interface-equipe/spec.md
- nova-evolucao-clinica: specs/registro-evolucao-clinica/spec.md
- novos-cadastros-visuais: specs/cadastro-paciente/spec.md, specs/cadastro-profissional/spec.md
- painel-administrativo-xano: specs/interface-painel-administrativo/spec.md
- painel-dentista-xano: specs/painel-profissional/spec.md
- painel-profissional-refino: specs/interface-painel-profissional/spec.md
- painel-recepcao-xano: specs/interface-painel-recepcao/spec.md
- procedimentos-realizados: specs/procedimentos-consulta-realizados/spec.md
- reagendar-consulta: specs/reagendamento-consulta/spec.md
- sessao-prolongada-equipe: specs/acesso-autenticado/spec.md
- smoke-contratos-xano: specs/smoke-contratos-xano/spec.md
- tela-agenda-xano: specs/agenda-consultas/spec.md, specs/interface-agenda/spec.md
- tela-nova-consulta-xano: specs/interface-nova-consulta/spec.md
- tela-pacientes-xano: specs/interface-pacientes/spec.md, specs/roteamento-equipe-conectada/spec.md
- tela-procedimentos-xano: specs/catalogo-procedimentos/spec.md
- tela-profissionais-xano: specs/listagem-profissionais/spec.md
- tela-prontuario-xano: specs/interface-prontuario/spec.md
