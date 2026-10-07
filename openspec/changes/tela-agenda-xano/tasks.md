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

## 3. Revisão e publicação

- [x] 3.1 Criar testes unitários Python e JavaScript por contrato GET/POST novo ou alterado e cenários de autorização, validação e conflito.
- [x] 3.2 Executar verificações aplicáveis, validar OpenSpec e revisar diff integral e referência visual.
- [x] 3.3 Executar dry-run Xano somente para arquivos desta change, revisar saída e publicar schemas/rotas sem registros.
- [ ] 3.4 Conferir manualmente Agenda conectada em contas de Administrador, Recepcionista e Profissional e registrar questões residuais para revisão.
