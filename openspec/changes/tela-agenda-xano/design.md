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
- Criar `GET /agenda/opcoes` dedicado à Administração e Recepção, retornando somente `{id, nome}` de cadastros ativos. Não reutilizar `GET /pacientes`, que retorna mais dados pessoais.
- Enriquecer `GET /consultas` com rótulos administrativos seguros e Procedimentos sem multiplicar linhas de Consulta.
- Tornar `consulta.procedimento_id` legado opcional e preenchê-lo com o primeiro Procedimento quando houver; a relação múltipla canônica é `consulta_procedimento`.
- A tela não cria nem bloqueia horários. Gestão de Disponibilidades fica fora do escopo.
- Datas usam `America/Sao_Paulo`; limites diários são convertidos em timestamps e o Xano valida conflitos e autorização.
- Respostas REST serializam campos `timestamp` como texto ISO 8601 em UTC para manter o contrato consumido pelo Streamlit (`datetime.fromisoformat`).
- Situação só é atualizada na interface após sucesso do Xano; cancelamento exige motivo e preserva histórico.

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
