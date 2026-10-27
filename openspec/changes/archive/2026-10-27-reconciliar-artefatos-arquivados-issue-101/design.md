## Método OpenSpec e limites

O CLI instalado é OpenSpec 1.10.0. Ele não possui comando `sync`; `openspec archive` é o fluxo oficial suportado que atualiza `openspec/specs/` e move a change ativa para `openspec/changes/archive/`. O comando recusa uma pasta de destino arquivada já existente. Portanto, ele não pode repor diretamente um arquivo dentro do diretório arquivado `2026-10-02-retomada-cadastro-profissional-admin`. Para não reescrever os outros artifacts históricos, esta change mantém a recuperação da spec como artifact ativo e registra a reposição pontual do delta histórico depois do archive desta change.

A reconciliação usa somente 39 diretórios com artifacts versionados nesta árvore: 38 possuem um ou mais `specs/<capacidade>/spec.md`, e `2026-10-02-retomada-cadastro-profissional-admin` é a única change versionada sem spec. Há 14 nomes de diretórios vazios locais no ambiente de referência que não aparecem no Git index e não têm proposal/design/tasks; eles não são tratados como changes e não recebem requisitos inventados. `git status --untracked-files=all`, enumeração recursiva, verificação de reparse points e `git ls-tree -r HEAD` foram usados para distinguir arquivos do repositório e diretórios vazios do ambiente.

## Inventário capability → arquivo principal

Foram encontrados 30 caminhos de capability nos deltas arquivados. Antes da reconciliação, o arquivo principal existia para 5 e faltava para 25. A CLI criou os 25 specs principais com 71 requirements recuperados dos deltas. Nos cinco caminhos principais existentes havia 49 títulos arquivados; 42 já tinham correspondência literal e sete exigiram classificação semântica. Após a CLI, dois títulos com evidência foram adicionados ao spec principal e cinco ficaram cobertos por requisito/capability equivalente. No conjunto das 38 changes de origem e da delta restaurada de 02/10, há 110 pares únicos capability/requisito: 105 títulos constam literalmente no spec principal e cinco foram classificados como equivalentes, sem reaplicar texto redundante.

| Capability | Deltas arquivados | Spec principal | Requirements ADDED/MODIFIED/REMOVED (títulos) | Estado |
|---|---:|---|---|---|
| acesso-autenticado | 6 | presente | 9/7/0 | 8/9 headings exatos; login separado do Paciente coberto por `Acesso inicial` e pelo entrypoint `autoatendimento-paciente` |
| agenda-consultas | 2 | criado pela CLI | 9/0/0 | 9 requisitos adicionados; cobre leitura e manutenção de Disponibilidades |
| autoatendimento-paciente | 1 | criado pela CLI | 5/0/0 | 5 requisitos adicionados |
| cadastro-paciente | 2 | presente | 7/0/0 | 6/7 headings exatos; apresentação visual coberta por `interface-equipe` |
| cadastro-profissional | 3 | presente | 8/0/0 | 7/8 headings exatos; apresentação visual geral coberta por `interface-equipe`; modal responsivo adicionado |
| catalogo-procedimentos | 1 | ausente | 1/0/0 | Adicionar 1 requisito |
| consulta-contas-acesso | 1 | ausente | 2/0/0 | Adicionar 2 requisitos |
| consultas | 1 | ausente | 2/0/0 | Adicionar 2 requisitos |
| consultas-do-paciente | 1 | ausente | 1/0/0 | Adicionar 1 requisito |
| edicao-paciente | 2 | ausente | 6/0/0 | Adicionar 6 requisitos |
| execucao-local-multiplataforma | 1 | presente | 2/0/0 | 2/2 headings refletidos |
| exames | 1 | ausente | 4/0/0 | Adicionar 4 requisitos |
| gestao-disponibilidades | 1 | ausente | 2/0/0 | Adicionar 2 requisitos |
| gestao-profissionais | 1 | ausente | 3/0/0 | Adicionar 3 requisitos |
| interface-agenda | 1 | ausente | 3/0/0 | Adicionar 3 requisitos |
| interface-equipe | 7 | presente | 11/5/0 | Navegação sticky adicionada; leitura/manutenção de Disponibilidades ficam na capability `agenda-consultas`; responsividade geral coberta pelas regras vigentes e pela capability específica de Nova Consulta |
| interface-nova-consulta | 1 | ausente | 2/0/0 | Adicionar 2 requisitos |
| interface-pacientes | 1 | ausente | 3/0/0 | Adicionar 3 requisitos |
| interface-painel-administrativo | 1 | ausente | 2/0/0 | Adicionar 2 requisitos |
| interface-painel-profissional | 1 | ausente | 3/0/0 | Adicionar 3 requisitos |
| interface-painel-recepcao | 1 | ausente | 2/0/0 | Adicionar 2 requisitos |
| interface-prontuario | 1 | ausente | 2/0/0 | Adicionar 2 requisitos |
| listagem-profissionais | 1 | ausente | 1/0/0 | Adicionar 1 requisito |
| painel-profissional | 1 | ausente | 1/0/0 | Adicionar 1 requisito |
| procedimentos-consulta-realizados | 1 | ausente | 3/0/0 | Adicionar 3 requisitos |
| reagendamento-consulta | 1 | ausente | 4/0/0 | Adicionar 4 requisitos |
| registro-clinico | 1 | ausente | 4/0/0 | Adicionar 4 requisitos |
| registro-evolucao-clinica | 1 | ausente | 1/0/0 | Adicionar 1 requisito |
| roteamento-equipe-conectada | 1 | ausente | 3/0/0 | Adicionar 3 requisitos |
| smoke-contratos-xano | 1 | ausente | 2/0/0 | Adicionar 2 requisitos |

Os 25 arquivos principais ausentes agrupam 71 headings `Requirement`. A contagem de 49 corresponde apenas aos headings nas cinco capabilities com arquivo principal; não é o total geral de todos os deltas.

## Classificação dos sete títulos sem correspondência literal

| Título delta | Estado nesta reconciliação | Evidência e destino |
|---|---|---|
| `Login independente do Paciente` | Coberto por requisitos posteriores com nome mais específico; não duplicar | `openspec/specs/acesso-autenticado/spec.md`, requisito “Acesso inicial limitado à própria identificação”, cenário “Equipe separada de Paciente”, delimita login interno; a capability `autoatendimento-paciente` tem requisito “Sessão independente do Paciente” para o entrypoint separado. |
| `Menu da equipe fixo durante a rolagem em telas largas` | Atual; adicionar | `assets/estilos.css` define coluna sticky; `tests/visual/conferir_agenda_ficticia.py` verifica sticky em viewport larga e menu estático em estreita. Delta fonte: `archive/corrigir-edicao-paciente-menu-fixo/specs/interface-equipe/spec.md`. |
| `Visualizar Disponibilidades na Agenda` | Coberto por requisito de capability mais específica; não duplicar na interface geral | Delta `agenda-consultas` inclui “Consultar disponibilidades da Agenda” e “Consulta administrativa da agenda”; destino consolidado `openspec/specs/agenda-consultas/spec.md`. |
| `Manter Disponibilidades pela Agenda` | Coberto por requisito de capability mais específica; não duplicar na interface geral | Delta `agenda-consultas` inclui “Administrar Disponibilidades da Agenda” e “Alterar Disponibilidade livre”; destino consolidado `openspec/specs/agenda-consultas/spec.md`. |
| `Layout responsivo e acessível` (MODIFIED) | Coberto por requisitos vigentes e específicos; não duplicar | `openspec/specs/interface-equipe/spec.md` mantém responsividade/acessibilidade; `interface-nova-consulta` especifica o fluxo responsivo do formulário. |
| `Apresentação visual do cadastro de Paciente` | Coberto por requisito visual transversal mais recente; não duplicar | `openspec/specs/interface-equipe/spec.md`, “Identidade visual das telas existentes”; delta posterior `archive/2026-10-01-recriacao-layout-sorriso-mais/specs/interface-equipe/spec.md`. |
| `Apresentação visual do cadastro de Profissional` | Coberto por requisito visual transversal mais recente; não duplicar | `openspec/specs/interface-equipe/spec.md`, “Identidade visual das telas existentes”; delta posterior `archive/2026-10-01-recriacao-layout-sorriso-mais/specs/interface-equipe/spec.md`. |

O modal responsivo é um requisito distinto e atual, por isso foi adicionado a `cadastro-profissional`: `assets/estilos.css` define área rolável e limites de viewport; o delta original está em `archive/cadastro-profissional-refino/specs/cadastro-profissional/spec.md`.

## Delta recuperado da retomada de 02/10

A retomada arquivada registra que corrigiu divergência reproduzida do rótulo de retorno para “Voltar”, e `tests/test_profissionais.py` verifica o botão e seu fluxo nas linhas 307–308. O texto normativo vem sem alteração do requisito “Formulário da equipe separado de pacientes” em `archive/cadastro-profissional-admin/specs/cadastro-profissional/spec.md`; a versão vigente já contém esse cenário. A delta foi restaurada em `archive/2026-10-02-retomada-cadastro-profissional-admin/specs/cadastro-profissional/spec.md` com essa redação, sem requisito inventado. A CLI não oferece emenda de diretório arquivado existente; esta reposição pontual ocorre depois do fluxo de sincronização da change ativa, mantendo proposal/design/tasks históricos intactos.

## Resultado da sincronização

`openspec archive --yes reconciliar-artefatos-arquivados-issue-101` criou `archive/2026-10-27-reconciliar-artefatos-arquivados-issue-101` e sincronizou oficialmente os 25 arquivos principais ausentes, além de adicionar a regra de menu a `interface-equipe` e o requisito de modal responsivo a `cadastro-profissional`. A seção de cadastro com o rótulo “Voltar” já estava refletida na principal e, por isso, a CLI não aplicou alteração duplicada. Foram validados 30 specs de capability e a change ainda ativa `integrar-telas-orfas`; todos passaram em strict.

O CLI avisou que esta change possui mais de dez deltas e que foi arquivada com tarefas incompletas (7/13 no momento da execução). Isso ocorreu porque algumas tarefas posteriores dependiam do próprio archive. A lista foi atualizada após a conclusão dessas etapas e o diff registra evidências; não houve alteração de tasks históricas de outras changes.

## Pendências históricas mantidas abertas

Permanecem abertas as tasks 1.2 e 4.4 de `archive/2026-09-30-cadastro-paciente-equipe` (Issue própria e revisão processual ausentes) e 2.2a, 2.3a e 2.4a de `archive/cadastro-profissional-admin` (testes e inspeção remota no Xano sem evidência). Esta change não muda seus checkboxes. Nenhum arquivo de spec principal é escrito manualmente; a integração é feita por `openspec archive`.
