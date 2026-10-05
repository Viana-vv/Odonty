## Context

Ver `proposal.md` para a motivação e `specs/` para os contratos esperados. O pull read-only do workspace 149129/branch `v1` encontrou `consulta` sem Disponibilidade e com apenas `procedimento_id`; `prontuario` é uma estrutura legada com procedimento e observações, enquanto `prontuario_paciente` representa o prontuário único. Não foram encontrados schemas ou endpoints de Agenda, Registro Clínico e Exame. Nenhuma linha de dados foi consultada.

## Goals / Non-Goals

**Goals:**

- Manter autenticação, autorização, validações, transações e proteção do histórico no Xano.
- Acrescentar relações de disponibilidade e Consulta sem apagar nem reinterpretar registros legados.
- Separar Registro Clínico do Prontuário, preservando autoria, vínculos e histórico de correções.
- Revisar contratos, compatibilidade e plano de migração com o grupo antes do Apply.

**Non-Goals:**

- Criar ou refazer telas Streamlit nesta change.
- Implementar APIs de Exame, pagamentos, edição de Profissional ou prontuário do Paciente.
- Migrar, corrigir ou apagar registros existentes sem auditoria autorizada e estratégia aprovada.
- Publicar mudanças no workspace antes de aprovar contratos, permissões e testes.

## Decisions

### Separar Disponibilidade, Consulta e Registro Clínico

Criar uma estrutura própria para Disponibilidade da Agenda e uma estrutura `registro_clinico` vinculada a Prontuário, Paciente, Profissional e, opcionalmente, Consulta. A alternativa de continuar usando `consulta` como agenda ou `prontuario` como Registro Clínico mistura entidades que o modelo de domínio mantém separadas.

### Preservar estruturas e relações legadas

Manter a tabela `consulta` e seus campos existentes, permitindo `procedimento_id` nulo para novas Consultas sem Procedimento; os valores históricos permanecem intactos. Adicionar vínculo de novas Consultas à Disponibilidade e uma relação N:N para Procedimentos; quando houver Procedimentos, o primeiro também preenche o campo legado. Não inferir nem converter silenciosamente dados antigos. `prontuario_paciente` permanece o prontuário único do Paciente, e a tabela legada `prontuario` não será renomeada nem removida nesta change.

### Garantir conflitos no backend

O Xano validará sessão, situação e perfil em todas as rotas. A reserva da Disponibilidade e a criação da Consulta ocorrerão atomicamente. Como a regra também envolve intervalos sobrepostos e concorrência, o desenho físico final deverá demonstrar uma garantia transacional no workspace de teste; uma consulta prévia sem proteção contra corrida não será aceita como controle suficiente.

### Isolar conteúdo clínico

As respostas administrativas de Consulta não incluirão campos de Registro Clínico. Endpoints clínicos terão escopo próprio e validarão vínculo entre Conta de Acesso, Profissional, Consulta, Paciente e Prontuário. Histórico de requisições ficará desativado para dados clínicos e falhas terão mensagens sanitizadas.

### Revisar contratos antes do Apply

O grupo aprovou os caminhos e a forma dos contratos abaixo em 02/10/2026. A implementação seguirá essa lista; respostas de listagem usam 200, criação usa 201, atualização usa 200, validação inválida usa 400, sessão ausente/inválida usa 401, escopo negado usa 403, recurso fora do escopo usa 404 e conflito de agenda usa 409.

| Método e caminho | Entrada | Autorização e resultado |
| --- | --- | --- |
| `GET /disponibilidades` | `profissional_id`, `inicio`, `fim` como filtros de consulta | Conta autenticada; retorna apenas horários futuros livres de Profissionais ativos. |
| `POST /disponibilidades` | `profissional_id`, `inicio`, `fim` | Profissional ativo na própria agenda ou Administrador/Recepcionista autorizados; cria intervalo livre sem sobreposição. |
| `PATCH /disponibilidades/{id}` | `inicio`, `fim` ou `situacao` nos limites definidos na spec | Mesmo escopo da criação; permite bloquear/desbloquear somente intervalos futuros livres. Intervalo reservado não pode ser editado ou liberado diretamente. |
| `POST /consultas` | `paciente_id`, `disponibilidade_id`, `procedimento_ids` (pode ser vazio) e motivo opcional | Somente Administrador/Recepcionista autorizados agendam para um Paciente. O Xano valida o Paciente e os Procedimentos informados, deriva o Profissional da Disponibilidade e persiste a operação atomicamente. |
| `GET /consultas` | Filtros opcionais `paciente_id`, `profissional_id`, `situacao`, `inicio`, `fim` | Paciente recebe suas Consultas passadas e futuras; o Xano deriva seu identificador da sessão e ignora/rejeita filtro de outro Paciente. Profissional e equipe administrativa recebem apenas o próprio escopo autorizado; listagens administrativas não contêm dados clínicos. |
| `PATCH /consultas/{id}/situacao` | `situacao` e `motivo_cancelamento` quando aplicável | Aplica apenas as transições e os perfis autorizados definidos na spec, registra responsável/data/motivo e preserva o histórico. Paciente não pode alterar situação. |
| `POST /registros-clinicos` | `paciente_id`, `consulta_id` opcional, conteúdo clínico e `liberado_paciente` (padrão `false`) | Somente Profissional ativo autorizado; vínculos são resolvidos e conferidos no Xano. |
| `GET /registros-clinicos` | Filtros opcionais `paciente_id`, `consulta_id` | Profissional recebe registros do escopo de atendimento; Paciente recebe somente registros próprios com `liberado_paciente=true`; perfil administrativo não recebe conteúdo clínico. |
| `POST /registros-clinicos/{id}/retificacoes` | Novo conteúdo e `justificativa` | Somente Profissional autorizado; adiciona retificação imutável vinculada ao registro original, sem sobrescrever o conteúdo anterior. |

Todas as rotas protegidas validam sessão, estado e perfil no Xano. Recursos fora do escopo respondem 404 para evitar confirmar sua existência. Nenhum endpoint específico será publicado por inferência a partir do nome atual das tabelas.

As respostas de sucesso usam a chave de recurso prevista no cliente REST: `{ "disponibilidades": [...] }`, `{ "disponibilidade": {...} }`, `{ "consultas": [...] }`, `{ "consulta": {...} }`, `{ "registros_clinicos": [...] }`, `{ "registro_clinico": {...} }` e `{ "retificacao": {...} }`. Erros usam `{ "codigo": "<código estável>", "mensagem": "<mensagem segura>" }`, padrão já adotado pelo grupo Sorriso Acesso. Os códigos HTTP são 200 para consulta/atualização, 201 para criação, 400 para entrada inválida, 401 para sessão ausente ou inválida, 403 para perfil sem permissão, 404 para recurso inexistente ou fora do escopo e 409 para conflito. Mensagens não incluem conteúdo clínico, credenciais nem detalhes internos.

A API apresenta `Realizada` para Consulta armazenada com situação legada `Concluída`. As demais situações da API mantêm os valores aceitos pela tabela `consulta`; a tradução evita alterar registros históricos ou remover valores do enum legado.

### Definir transições e responsáveis da Consulta

O Xano aceita somente as transições `agendada → confirmada`, `agendada → cancelada`, `confirmada → em atendimento`, `confirmada → cancelada`, `confirmada → falta` e `em atendimento → realizada`. Profissional, Administrador ou Recepcionista podem confirmar e cancelar dentro do próprio escopo; somente Profissional autorizado pode iniciar atendimento, concluir Consulta ou registrar falta. O Paciente não agenda nem altera a situação. O cancelamento exige motivo e grava uma linha append-only em `consulta_situacao_historico` com situação anterior/nova, Conta de Acesso responsável, data e motivo. A Consulta e seu horário original permanecem no histórico; se a Disponibilidade ainda for futura, ela volta a ficar livre. Uma Disponibilidade pode, ao longo do tempo, estar vinculada a várias Consultas históricas, mas no máximo uma ativa; o vínculo de cada Consulta cancelada permanece preservado. Estados finais não podem ser reabertos por esse endpoint.

### Restringir alteração de Disponibilidade

`PATCH /disponibilidades/{id}` aceita alteração do intervalo ou da situação entre `disponível` e `bloqueado` somente quando a Disponibilidade estiver livre e futura. `reservado` e `indisponível` são controlados pelo fluxo de agendamento/cancelamento. Para mudar intervalo reservado, a Consulta deve ser cancelada por Conta de Acesso autorizada; a alteração posterior segue as mesmas regras de escopo e sobreposição da criação.

### Resolver Paciente e Consultas pela sessão

Em `GET /consultas`, o Xano resolve a associação entre Conta de Acesso e Paciente autenticado. Filtros enviados pelo Paciente não ampliam o escopo; `paciente_id` ausente retorna as Consultas próprias e um identificador divergente é rejeitado ou ignorado sem revelar dados de terceiros. O `POST /consultas` não é disponível ao perfil Paciente.

Em retificações, `liberado_paciente` herda o valor do Registro Clínico original. A retificação não pode ampliar a visibilidade. Nova liberação depende de operação autorizada separada, fora do endpoint de retificação.

## Risks / Trade-offs

- **Consulta legada exige um procedimento e não aponta para Disponibilidade** → manter os dados atuais, introduzir relações aditivas e só ajustar obrigatoriedade após teste de compatibilidade.
- **Corrida entre agendamentos simultâneos** → validar reserva atômica e conflitos sobrepostos em integração Xano com dados fictícios antes da publicação.
- **Mapeamento de prontuário legado pode expor conteúdo clínico** → não ler registros reais; restringir testes a dados fictícios e decidir migração separadamente após revisão.
- **Permissões clínicas são mais restritas que permissões administrativas** → especificar testes diretos para todos os perfis e validar autorização no backend.

## Migration Plan

1. Revisar este contrato e confirmar a matriz de permissões antes do Apply.
2. Reinspecionar schemas publicados e construir alterações aditivas em branch de teste do Xano.
3. Executar testes locais sem rede e testes reais opt-in apenas com contas e registros fictícios; comprovar conflitos, rollback e isolamento de perfis.
4. Publicar após revisão do grupo, preservando as tabelas e o histórico legados.
5. Em reversão, desabilitar as novas rotas sem apagar Disponibilidades, Consultas ou Registros Clínicos já criados.
