## 1. Contratos e backend Xano

- [x] 1.1 Confirmar schemas remotos de Consulta, Disponibilidade, Paciente, Profissional e Procedimento e identificar estruturas ausentes.
- [x] 1.2 Implementar/ajustar schemas de disponibilidade, vínculo consulta-disponibilidade, vínculo consulta-procedimento, histórico de situação e controle de concorrência sem apagar histórico.
- [x] 1.3 Ajustar criação de Consulta para aceitar nenhum ou vários Procedimentos ativos e manter reserva e conflito atômicos.
- [x] 1.4 Enriquecer GET `/consultas` com datas e nomes administrativos seguros, sem duplicar Consultas.
- [x] 1.5 Criar GET `/agenda/opcoes` para Administração/Recepção, retornando somente IDs e nomes de cadastros ativos.
- [x] 1.6 Conferir transições, motivo obrigatório no cancelamento, liberação de horário e histórico.

## 2. Cliente e interface

- [x] 2.1 Adaptar cliente REST e validação dos contratos para campos de exibição e opções.
- [x] 2.2 Implementar carregamento conectado da lista diária, opções e Disponibilidades.
- [x] 2.3 Construir lista responsiva com filtros, busca, navegação por data, ordenação, estados vazios/erro e ações autorizadas.
- [x] 2.4 Implementar formulário de nova Consulta e ações de situação com confirmação e tratamento de conflitos.
- [x] 2.5 Habilitar Agenda na navegação conectada e remover aviso de integração indisponível.
- [x] 2.6 Manter os formulários de Consulta e Disponibilidade exclusivos entre si e separar a data do cadastro do filtro diário; validar troca nos dois sentidos, horários para a data interna e atualização da Agenda após sucesso.
- [x] 2.7 Atualizar a situação da Consulta antes da leitura da Agenda, evitando uma segunda recarga e cartões repetidos; verificar transição para Em atendimento com duas Consultas fictícias.

## 3. Revisão e publicação

- [x] 3.1 Criar testes unitários Python e JavaScript por contrato GET/POST novo ou alterado e cenários de autorização, validação e conflito.
- [x] 3.2 Executar verificações aplicáveis, validar OpenSpec e revisar diff integral e referência visual.
- [x] 3.3 Executar dry-run Xano somente para arquivos desta change, revisar saída e publicar schemas/rotas sem registros.
- [ ] 3.4 Conferir manualmente Agenda conectada em contas de Administrador, Recepcionista e Profissional e registrar questões residuais para revisão.
  - Registro (07/10/2026): os GETs de Agenda respondem 200 e existe uma Disponibilidade fictícia em 08/10/2026 às 09h. A conferência manual na interface ainda não foi feita; a conta de Recepcionista foi usada somente nos smoke tests da API. Administrador e Profissional também estão pendentes.

- Registro (07/10/2026): o smoke test real do POST /consultas com a Recepcionista e cadastros fictícios encontrou a falha Invalid pipe, confirmou a correção publicada e retornou HTTP 201. Foi mantida uma Disponibilidade livre em 08/10/2026 às 10h para verificação pela interface. A conferência visual dos perfis segue pendente.

- Registro (07/10/2026): após o smoke test inicial com HTTP 201, a interface reportou erro em uma tentativa seguinte. A rota foi ajustada para incrementar diretamente os contadores de concorrência existentes e republicada. A disponibilidade das 10h continuava livre; falta confirmar novo POST e a inspeção visual dos perfis.

- Registro (08/10/2026): a Recepção agendou uma Consulta em 08/10, mas a Agenda mostrou estado vazio. A rota GET /consultas foi corrigida e publicada; a verificação pela API retornou três Consultas em 08/10 às 09h, 10h e 11h. Falta atualizar a tela conectada na sessão da Recepção e concluir a inspeção manual dos outros perfis.

- Registro (08/10/2026): PATCH de situaÃ§Ã£o corrigido e publicado apÃ³s remover pipes default que podiam interromper o cancelamento. ValidaÃ§Ã£o real com cancelamento permanece pendente para nÃ£o alterar Consulta sem escolha explÃ­cita do usuÃ¡rio.
