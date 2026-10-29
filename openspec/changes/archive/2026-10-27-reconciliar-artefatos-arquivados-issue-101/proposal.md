## Why

A inspeção dos arquivos versionados encontrou 39 changes arquivadas, 38 com delta spec, 30 capabilities históricas e somente cinco specs principais. A especificação vigente precisa consolidar os 25 caminhos de capability ausentes a partir dos requisitos arquivados, sem recuperar requisitos substituídos. A retomada de cadastro profissional também foi arquivada sem delta spec, embora tenha corrigido a ação “Voltar” conforme o requisito de origem.

## What Changes

- Adicionar à change ativa um delta para cada uma das 25 capabilities cujo arquivo principal está ausente, reunindo os requisitos aprovados e não conflitantes encontrados nas 38 specs arquivadas.
- Atualizar deltas das capacidades principais existentes para os requisitos comprovadamente atuais: menu fixo da equipe e modal responsivo do cadastro de Profissional.
- Registrar os outros cinco títulos ausentes como cobertos, absorvidos ou substituídos por requisitos posteriores, com referências concretas no design.
- Arquivar esta change pela CLI OpenSpec para integrar os deltas a `openspec/specs/` sem edição manual.
- Restaurar o registro documental da correção “Voltar” para a change histórica, mantendo as evidências e limites do CLI registrados.

Fora do escopo: mudanças funcionais, testes remotos no Xano, criação de tarefas/changes para diretórios vazios não versionados, e marcação retrospectiva de tarefas sem evidência.

## Capabilities

### New Capabilities

`agenda-consultas`, `autoatendimento-paciente`, `catalogo-procedimentos`, `consulta-contas-acesso`, `consultas`, `consultas-do-paciente`, `edicao-paciente`, `exames`, `gestao-disponibilidades`, `gestao-profissionais`, `interface-agenda`, `interface-nova-consulta`, `interface-pacientes`, `interface-painel-administrativo`, `interface-painel-profissional`, `interface-painel-recepcao`, `interface-prontuario`, `listagem-profissionais`, `painel-profissional`, `procedimentos-consulta-realizados`, `reagendamento-consulta`, `registro-clinico`, `registro-evolucao-clinica`, `roteamento-equipe-conectada` e `smoke-contratos-xano`.

### Modified Capabilities

- `interface-equipe`: adicionar navegação sticky já implementada e verificada.
- `cadastro-profissional`: registrar o requisito de modal responsivo e a correção da ação “Voltar”.

## Impact

Artefatos OpenSpec. `openspec archive --yes reconciliar-artefatos-arquivados-issue-101` aplicará os deltas aos specs principais e arquivará esta change. A spec histórica ausente de 02/10 será restaurada separadamente após o arquivo ativo, conforme método e limitação documentados.
