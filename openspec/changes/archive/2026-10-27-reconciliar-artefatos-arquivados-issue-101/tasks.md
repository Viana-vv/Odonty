## 1. Inventário e evidências

- [x] 1.1 Inventariar changes arquivadas versionadas e seus deltas: 39 changes, 38 com spec e uma ausente.
- [x] 1.2 Agrupar requisitos: 30 capabilities; antes da reconciliação, 25 não tinham spec principal; cinco já existiam. Os 49 headings dos cinco specs vigentes tinham 42 correspondências exatas.
- [x] 1.3 Classificar os sete títulos sem correspondência literal pelo estado atual e pela fonte posterior, sem tratar divergência de título como ausência automática.
- [x] 1.4 Registrar limites físicos: 14 nomes de diretórios vazios informados no ambiente de referência não pertencem aos 39 diretórios versionados; não criar artifacts para eles.

## 2. Reconciliação OpenSpec

- [x] 2.1 Criar nesta change os deltas para as 25 capabilities sem arquivo principal, reunindo 71 requisitos ADDED dos deltas arquivados, sem duplicar headings.
- [x] 2.2 Adicionar `interface-equipe` com navegação sticky, comprovada em `assets/estilos.css` e `tests/visual/conferir_agenda_ficticia.py`.
- [x] 2.3 Atualizar `cadastro-profissional` com modal responsivo comprovado no CSS e manter “Voltar” conforme requisito original e teste existente.
- [x] 2.4 Validar a change com `openspec validate reconciliar-artefatos-arquivados-issue-101 --strict` antes do archive.
- [x] 2.5 Arquivar pela CLI com `openspec archive --yes reconciliar-artefatos-arquivados-issue-101`; a CLI criou o archive datado e sincronizou 27 capabilities (25 novas, duas atualizadas).
- [x] 2.6 Restaurar o delta ausente no caminho histórico de 02/10 com a redação da spec original, preservando proposal/design/tasks.
- [x] 2.7 Validar após sincronização com `openspec validate --all --strict --no-interactive`: 31 itens passaram; comparação final encontrou 30 capabilities vigentes, 105/110 pares únicos com heading idêntico e cinco cobertos semanticamente, conforme design.

## 3. Revisão e entrega

- [x] 3.1 Atualizar Issue #101 com inventário, resultados e limites desta árvore.
- [x] 3.2 Revisar o diff documental, validar `git diff --check` e registrar commits nesta branch.
