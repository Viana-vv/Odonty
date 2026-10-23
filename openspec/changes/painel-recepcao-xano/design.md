## Contexto

Consulte `proposal.md` e `specs/interface-painel-recepcao/spec.md`. A Visão geral conectada é renderizada dentro de `paginas_equipe.py`; a Agenda usa `ClienteXano.listar_consultas`, que chama o `GET /consultas` do Xano. Essa rota verifica sessão e perfil no backend, restringe o escopo do Profissional e retorna somente nomes, identificadores, horário, situação e rótulos de Procedimento. O painel deve usar o mesmo contrato e renderizar um subconjunto seguro dos campos.

## Objetivos / Não objetivos

**Objetivos:**
- Preencher o painel diário da Recepção com dados atuais do Xano e controles de atualização.
- Evitar requisições redundantes durante reruns e impedir que um resumo de outra sessão ou de outro dia seja reutilizado.
- Preservar o comportamento da Visão geral para os demais perfis.

**Não objetivos:**
- Alterar rotas, autorização, tabelas ou regras de negócio no Xano.
- Reproduzir a métrica de Pacientes ativos ou mostrar Procedimentos, observações, contatos ou conteúdo clínico.
- Implementar ou reconfigurar as áreas Agenda, Pacientes ou Nova Consulta.

## Decisões

- Para Recepcionista, carregar Consultas entre o início do dia atual e o início do próximo dia em `America/Sao_Paulo`, usando `listar_consultas(token, inicio, fim)`. Não introduzir um endpoint ou contrato paralelo: o Xano continua responsável por autenticar, autorizar e limitar resultados.
- Calcular total, realizadas e confirmadas a partir da lista retornada. Selecionar a próxima Consulta ativa por horário, excluindo Realizada, Cancelada e Falta. Ordenar a lista pelo horário e limitar a cinco.
- Normalizar, apenas para exibição do painel, o valor legado `Concluída` retornado pelo Xano para a situação de domínio `Realizada`; o contrato e os dados armazenados não são alterados.
- Renderizar somente horário, nome do Paciente, nome do Profissional e situação. Não renderizar Procedimentos embora o contrato os inclua, nem motivo administrativo ou campos clínicos.
- Manter um cache de 20 segundos na sessão Streamlit, associado ao hash da credencial e à data local do painel; oferecer atualização manual, que invalida o cache antes de carregar. Falhas não são armazenadas e, em falha de atualização, os dados anteriores não são apresentados.
- Respeitar respostas HTTP 429 com intervalo local de 20 segundos antes de permitir nova chamada, sem repetir a requisição em reruns consecutivos.
- Limpar o cache do painel junto aos demais dados de sessão em logout/expiração. Em 401, invalidar sessão e informar novo login; em 403, descartar cache e mostrar aviso de permissão sem dados técnicos. Outros erros exibem mensagem segura e controle de nova tentativa.
- Não efetuar GET `/agenda/opcoes` para construir o painel; o contrato traz listas de nomes desnecessárias para as métricas.
- Para o layout, usar quatro cartões de métricas, lista diária e coluna de atalhos baseada na referência. Substituir o cartão de Pacientes ativos da referência por Confirmadas hoje, pois a tela não deve requisitar dados adicionais.

## Riscos / Compensações

- O cache de 20 segundos pode mostrar brevemente uma agenda desatualizada → exibir horário de atualização e manter botão Atualizar para uma leitura imediata.
- A lista contém nomes de Pacientes → limitar a leitura ao perfil autorizado pelo Xano e não renderizar dados de contato ou detalhes clínicos.
- A situação pode mudar depois que a resposta é carregada → a Agenda continua fazendo a leitura autorizada própria e é o lugar de executar alterações de Consulta.

## Plano de implantação

Não há mudança de backend nem migração. A versão anterior pode ser restaurada revertendo somente os arquivos do painel e dos seus testes; remover a chave de cache da sessão também é seguro porque ela é transitória.
