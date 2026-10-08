# Design: Agenda conectada ao Xano

## Contexto

A navegação conectada desabilita Agenda. Existem contratos locais de Consulta e Disponibilidade, mas a lista não carrega nomes. A rota legada de Pacientes retorna dados pessoais além do necessário ao formulário. O workspace verificado não contém tabelas nem rotas da Agenda.

## Objetivos

- Habilitar Agenda diária conectada conforme referência aprovada do kit Sorriso Mais.
- Entregar agendamento e atualização de situação para perfis autorizados.
- Manter escopo e regras no Xano e minimizar dados pessoais recebidos pelo Streamlit.
- Criar somente estruturas ausentes, preservando dados e histórico.

## Decisões

- Lista diária ordenada por início, navegação entre datas, busca por Paciente/Procedimento e filtro por situação.
- Administrador e Recepcionista podem agendar. Profissional consulta sua própria agenda e recebe apenas ações compatíveis com o contrato de situação.
- O formulário usa Paciente e Profissional ativos, Disponibilidades livres e zero ou mais Procedimentos ativos. Telefone não é usado nem exibido.
- O filtro diário da Agenda e a data da Consulta são estados separados. O cadastro inicia com a data filtrada, mas sua própria data controla a busca de Disponibilidades; após o Xano confirmar o agendamento, a lista navega para o dia da Consulta criada.
- Os formulários de Consulta e Disponibilidade são mutuamente exclusivos. Os callbacks dos botões limpam o estado do formulário anterior antes de abrir o próximo.
- Criar `GET /agenda/opcoes` dedicado à Administração e Recepção, retornando somente `{id, nome}` de cadastros ativos. Não reutilizar `GET /pacientes`, que retorna mais dados pessoais.
- Enriquecer `GET /consultas` com rótulos administrativos seguros e Procedimentos sem multiplicar linhas de Consulta.
- Tornar `consulta.procedimento_id` legado opcional e preenchê-lo com o primeiro Procedimento quando houver; a relação múltipla canônica é `consulta_procedimento`.
- A tela permite cadastrar Disponibilidades para Administrador e Recepcionista; o Xano valida conflitos e autorização.
- Datas usam `America/Sao_Paulo`; limites diários são convertidos em timestamps e o Xano valida conflitos e autorização.
- Respostas REST serializam campos `timestamp` como texto ISO 8601 em UTC para manter o contrato consumido pelo Streamlit (`datetime.fromisoformat`).
- Situação só é atualizada na interface após sucesso do Xano; cancelamento exige motivo e preserva histórico.
- A atualização de situação roda no callback do botão antes de carregar a lista diária. Assim, a Agenda faz uma única leitura após a alteração e evita renderizar cartões antigos durante uma segunda recarga.

## Dados e migração

- Conferir schemas remotos antes de publicar. Criar somente se ausentes: `disponibilidade_agenda`, `consulta_disponibilidade`, `consulta_procedimento`, `consulta_situacao_historico` e `agenda_controle`.
- Preservar tabela `consulta`, dados, identificadores e campo legado `procedimento_id`; torná-lo anulável sem reescrever registros.
- Não enviar registros pelo CLI. Usar dry-run revisado e não usar `--force`, `--delete`, `--truncate` ou `--no-transaction`.

## Segurança

- Todas as rotas validam sessão, perfil e escopo no Xano.
- Listas não retornam telefone, CPF, observações administrativas ou conteúdo clínico.
- `GET /agenda/opcoes` é restrito a Administração e Recepção e minimiza os dados retornados.
- O frontend não substitui autorização no backend.

## Riscos e mitigação

- O CLI mostra somente a branch `v1 (live)`. O push altera o workspace usado pelo projeto, então ocorrerá apenas após revisar diff e dry-run.
- A relação consulta/procedimentos é muitos-para-muitos; os rótulos precisam ser agregados sem duplicar Consultas.
- Os arquivos locais podem divergir do Xano remoto. Comparar o pull atualizado e limitar arquivos incluídos no push.

## Questões em aberto

Nenhuma decisão funcional pendente. Antes da publicação, revisar se o dry-run inclui somente esta change e as operações de schema esperadas.


## Correções após validação em execução

- O Xano retornava HTTP 500 quando `format_timestamp` e `replace` eram usados no `eval` de `db.query`. A conversão das datas e a normalização de situação agora acontecem após a consulta.
- As expressões `not in` e o filtro `includes` também falhavam em execução nas rotas de Agenda. As validações usam comparações diretas; o escopo por perfil usa `intersect` e `count`.
- Os GETs publicados foram confirmados com HTTP 200. Um horário fictício foi criado para permitir a conferência manual do agendamento em 08/10/2026, às 09h.

- O POST /consultas publicado retornava Invalid pipe durante o agendamento. A busca de Procedimentos e a verificação de conflitos foram reescritas sem o operador de lista incompatível. O smoke test real de cadastro sem Procedimentos retornou HTTP 201.

- Na segunda tentativa de agendamento, o Xano ainda poderia falhar ao atualizar os contadores existentes de concorrência. O POST agora incrementa diretamente os campos com padrão 0, sem default; a publicação foi confirmada. A verificação real desse caminho repetido segue pendente.

- A interface preserva a mensagem segura da API para HTTP 429 ao carregar opções de agendamento, para informar quando a equipe deve aguardar antes de tentar novamente.

- Em 08/10/2026, o POST confirmou três Consultas, mas GET /consultas retornava uma lista vazia. A expressão com filtros opcionais e comparações de null no where omitia linhas existentes. A rota agora consulta os registros e aplica filtros e escopo no Xano antes de enriquecer os dados; a leitura sem filtro e a leitura diária retornaram as três Consultas.

- Em 08/10/2026, a RecepÃ§Ã£o relatou que o cancelamento nÃ£o concluÃ­a. O PATCH ainda usava default no motivo e nos contadores; essas expressÃµes foram removidas, a rota compilou e foi publicada no Xano. NÃ£o foi feito cancelamento real de teste para preservar as Consultas existentes.
