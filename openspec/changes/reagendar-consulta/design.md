## Context

Ver `proposal.md` para motivação e `specs/reagendamento-consulta/spec.md` para os comportamentos. A Issue #64 determina Consulta original histórica e nova Consulta na Disponibilidade escolhida. A inspeção dos exports encontrou:

- `consulta`: Paciente, Profissional, início/fim, situação, Procedimento legado opcional e observações;
- `consulta_disponibilidade`: uma linha única por Consulta; permite Consultas canceladas históricas na mesma Disponibilidade;
- `consulta_situacao_historico`: auditoria append-only de situação, responsável, data e motivo;
- `consulta_procedimento`: relação N:N sem atributo que distinga planejamento de realização;
- `agenda_controle`: linha única por escopo/identificador para serialização transacional;
- `consultas_POST.xs` e `consultas_id_situacao_PATCH.xs`: reserva/cancelamento transacionais com validação de sessão no Xano.

Não existe campo ou tabela para relação direta entre Consulta original e Consulta substituta. O grupo autorizou acrescentar esse vínculo explicitamente. Não foi feita consulta a dados de pacientes nem alteração em Xano na exploração.

## Goals / Non-Goals

**Goals:** compor o cancelamento permitido e a criação em uma transação; reutilizar contratos GET existentes e padrões visuais; implementar módulos isolados para integração pelo agente principal.

**Non-Goals:** alterar os módulos compartilhados `app.py`, `navegacao.py`, `paginas_equipe.py` e `sorrisomais/api.py`; copiar relações clínicas automaticamente; modificar o esquema além do vínculo aprovado; alterar outras rotas além da releitura transacional de Disponibilidade autorizada como dependência direta.

## Decisions

### Contrato proposto

`POST /consultas/{id}/reagendamento` recebe somente `disponibilidade_id` inteiro positivo e `justificativa` textual obrigatória de 1 a 1000 caracteres após remoção dos espaços externos. O Paciente vem da Consulta original e o Profissional vem da Disponibilidade de destino. A resposta 201 contém `consulta_original` Cancelada e `consulta` Agendada, com identificadores e vínculos administrativos mínimos, e `reagendamento_id`. Erros seguros: 400, 401, 403, 404, 409 e 503. Sem cache nem histórico de requisições.

### Vínculo aditivo aprovado

Criar `consulta_reagendamento` com `consulta_original_id` único, `consulta_nova_id` único, `conta_acesso_id`, `justificativa` e `criado_em`. Os dois identificadores apontam para `consulta`; a estrutura não altera registros anteriores. Inserir uma única linha imutável na mesma transação que cancela a original e cria a nova. Uma Consulta substituta poderá ser origem de outro reagendamento futuro; uma Consulta original já cancelada não poderá gerar duas substitutas. Índices únicos reforçam a rejeição de duplicação concorrente.

### Preservar relações existentes

Manter relações originais de Procedimentos, Exames e Registro Clínico na Consulta original. O modelo físico não diferencia Procedimento planejado e realizado; portanto sua transferência automática não pode ser inferida nesta change. A definição de eventual associação da nova Consulta não autoriza alterar as relações históricas.

### Concorrência

Adquirir as travas usadas pelas rotas existentes de agenda para os Profissionais de origem/destino em ordem determinística, além do Paciente; reler estado original, vínculos, Disponibilidades e conflitos após a serialização. Excluir somente o identificador original da checagem de sobreposição do destino. Só após validar tudo, criar a nova Consulta e o vínculo, cancelar a original, gravar auditoria e atualizar as Disponibilidades dentro de `db.transaction`. Exceções devem desfazer todas essas alterações. Uma consulta prévia sem proteção contra corrida não é suficiente.

A revisão encontrou uma corrida em `PATCH /disponibilidades/{id}`: a rota verificava situação antes da transação e podia sobrescrever um horário reservado enquanto aguardava a trava. O grupo autorizou a correção estritamente necessária: após a trava do Profissional, reler a Disponibilidade e rejeitar com 409 caso desapareça, fique reservada/indisponível/passada ou mude de Profissional, intervalo ou situação desde a leitura inicial. A edição só pode gravar depois dessa validação. Testes de regressão estruturais em Python/JavaScript verificam a ordem trava → releitura → comparação → gravação; não constituem execução concorrente no Xano.

Na retomada de validação, o grupo autorizou alinhar o PATCH ao schema remoto atual: a trava será a linha de `agenda_controle` com escopo Profissional, compartilhada com o reagendamento, sem usar `agenda_lock_version` em Profissional. Foi autorizada a criação de grupo temporário exclusivo, com cópias isoladas dos schemas e endpoints necessários, seguida da remoção dos objetos de teste. Nenhuma rota, schema ou registro do grupo Sorriso Acesso será alterado nesses testes.

### Interface

Usar `GET /agenda/opcoes`, `GET /consultas` e `GET /disponibilidades` existentes; filtrar visualmente Consultas Agendadas/Confirmadas e sempre revalidar no backend. Reutilizar limites locais de data, representação de horários e composição de seletores de Nova Consulta. Limpar seleções dependentes ao alterar filtros. Não executar cancelamento e novo agendamento como duas chamadas da interface.

## Revisão

O grupo decidiu incluir vínculo persistente explícito entre Consultas e preservar relações originais sem cópia. Proposta, especificação e desenho foram reconciliados com essa decisão antes do Apply. A tabela aditiva é a única alteração de esquema autorizada nesta change.

A correção da rota de Disponibilidade foi autorizada separadamente após identificação da corrida, sem alteração de contrato REST ou de regra de negócio.

## Risks / Trade-offs

- Corrida com agendamento, cancelamento ou bloqueio → usar as mesmas travas e verificar concorrência em grupo temporário Xano.
- Erro entre cancelamento e reserva → transação única com teste de rollback.
- Vínculo legado ausente ou inconsistente → rejeitar sem inferência histórica.
- Cópia indevida de informação clínica → preservar relações originais e limitar o fluxo a dados administrativos.

## Migration Plan

Após revisar os artefatos, implementar e validar sem rede. Criar a tabela aditiva e usar grupo Xano temporário para compilação, autorização, conflitos concorrentes e rollback com dados fictícios, aguardando três segundos entre chamadas. Nenhuma rota será publicada na API de produção nesta tarefa. A reversão desabilita somente a nova rota/interface; não apaga registros históricos.
