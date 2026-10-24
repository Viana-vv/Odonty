# Verificação de acesso ao Xano — 24/10/2026

## Resultado

A execução remota da tarefa 3.1 permanece bloqueada por ausência de ambiente temporário segregado identificado. Não foram executados compilação por importação, testes de autorização, concorrência ou rollback. Nenhum resultado local ou dry-run foi usado como substituto dessas verificações.

## Inspeção executada

Na branch `reagendar-consulta-64`, a inspeção começou após o commit `910f19d642b6406c1db990456c1ccdcc738f4ef3`, que removeu o acesso a `agenda_lock_version` do endpoint novo.

Os perfis locais `Sem Backup` e `codex-odonty` apontam para o workspace 149129; o segundo indica a branch Xano `v1`. Não foi identificado perfil, workspace ou grupo temporário dedicado à validação desta change. A inspeção read-only da listagem de grupos não encontrou grupo temporário configurado. Essa evidência não afirma que inexista outro ambiente fora da configuração acessível.

Foram realizadas somente quatro requisições de metadados, todas com HTTP 200 e espaçamento mínimo de 3,2 segundos entre os inícios das chamadas:

| Método | Caminho relativo de metadados | Finalidade |
| --- | --- | --- |
| GET | `/table` | Identificar os esquemas disponíveis, sem consultar conteúdo |
| GET | `/apigroup` | Identificar grupos e eventual alvo temporário |
| GET | `/table/883768` | Conferir exclusivamente o schema de Profissional |
| GET | `/apigroup/434156/api` | Identificar os contratos já presentes, sem executar endpoints |

A listagem confirma que a tabela `consulta_reagendamento` e a rota `POST /consultas/{id}/reagendamento` já existem no grupo principal. Nenhum desses objetos foi criado, alterado ou chamado nesta verificação. Não foram consultados registros de pacientes, conteúdo clínico, credenciais de Contas de Acesso nem histórico de requisições.

As credenciais locais foram usadas somente em memória para autenticar as leituras de metadados. Valores de tokens, senhas e chaves não foram exibidos nem incluídos nos artefatos.

## Incompatibilidade que precisa ser resolvida

O schema remoto de `profissional` não contém `agenda_lock_version`. O commit `910f19d` removeu essa trava do endpoint novo, que permanece usando `agenda_controle`. Entretanto, o export local `disponibilidades_id_PATCH.xs` ainda solicita e atualiza `agenda_lock_version`.

Portanto, não é possível declarar a compilação desse PATCH compatível com o schema atual nem afirmar que o PATCH e o reagendamento compartilham a mesma trava no desenho atual da branch. A proteção contra edição obsoleta precisa ser verificada após alinhar essa serialização. Nenhuma alteração adicional de esquema ou de rota foi presumida durante a tarefa de validação.

O problema foi informado à coordenação antes de prosseguir. O próximo passo depende de confirmar a estratégia de trava compatível e fornecer um alvo temporário segregado autorizado. Não foi criado um grupo no workspace principal para contornar a ausência desse alvo.

## Regressões locais executadas nesta tentativa

`python -m pytest tests/api_contracts/test_consultas_id_reagendamento_post.py tests/api_contracts/test_disponibilidades_patch.py -q`: 36 testes passaram, sem rede.

`node --test tests/js/api_contracts/consultas-id-reagendamento-post.test.mjs tests/js/api_contracts/disponibilidades-patch.test.mjs`: 5 verificações passaram. `openspec validate reagendar-consulta --strict` e `git diff --check` também passaram. Esses resultados não detectam a incompatibilidade com o schema remoto, pois os testes verificam contratos simulados e estrutura do export.

## Verificações ainda obrigatórias

Em ambiente temporário segregado, compilar os exports e executar os cenários já descritos no README: autorização, preservação do vínculo e das relações originais, conflitos de Paciente e Profissional, concorrência sobre a mesma Consulta e o mesmo destino, edição de Disponibilidade aguardando a reserva e falha induzida para comprovar rollback integral. O início de cada requisição deve respeitar intervalo mínimo de três segundos; concorrência pode ser exercitada mantendo a primeira execução aberta no servidor durante o início da segunda, usando instrumentação exclusiva de teste.

A tarefa 3.1 continua aberta. Nenhum PR, merge, publicação em produção ou alteração na branch `main` foi realizado.
