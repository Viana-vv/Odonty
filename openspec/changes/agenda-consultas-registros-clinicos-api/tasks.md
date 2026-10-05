## 1. Revisão dos contratos e compatibilidade

- [x] 1.1 Revisar com o grupo caminhos, métodos, payloads, respostas, estados e matriz de permissões definidos nas specs; proposta aprovada pelo usuário em 02/10/2026 e registrada no design antes de iniciar alterações no Xano.
- [x] 1.2 Confirmar o mapeamento das tabelas legadas sem ler registros reais e definir migração aditiva; pull read-only do workspace 149129 confirmou `consulta` sem vínculo com Disponibilidade e com um único `procedimento_id`, além das estruturas legadas de Prontuário. Nenhum registro foi lido; o design preserva as tabelas e relações antigas sem conversão ou exclusão.

## 2. Disponibilidades e Consultas no Xano

- [x] 2.1 Criar as estruturas Xano de Disponibilidade, vínculo histórico, auditoria de situação e relação N:N para Procedimentos; tornar `procedimento_id` legado opcional sem alterar valores existentes. O pull read-only confirmou as referências e o dry-run reconheceu os esquemas.
- [x] 2.2 Implementar GET de Disponibilidades com filtros, escopo e exclusão de horários indisponíveis; contratos Python/JavaScript executados sem chamadas reais à rede.
- [x] 2.3 Implementar criação e alteração de Disponibilidade com autorização no Xano; contratos Python/JavaScript executados sem chamadas reais à rede. Cenários de integração ficam em 4.2.
- [x] 2.4 Implementar agendamento administrativo atômico de Consulta e reserva da Disponibilidade; contratos Python/JavaScript executados sem chamadas reais à rede. Concorrência, rollback e vínculos no Xano ficam em 4.2.
- [x] 2.5 Implementar listagem de Consultas por perfil e transições autorizadas, incluindo leitura restrita das Consultas do Paciente, proibição de agendamento/cancelamento pelo Paciente, auditoria e liberação do horário futuro ao cancelar. Contratos Python/JavaScript executados sem chamadas reais à rede; integração fica em 4.2.

## 3. Registros Clínicos

- [x] 3.1 Criar estruturas separadas para Registro Clínico e retificação, relacionadas a Prontuário, Paciente, Profissional e Consulta, preservando as tabelas legadas; esquemas reconhecidos no dry-run.
- [x] 3.2 Implementar POST de Registro Clínico com autorização no Xano e validação dos vínculos; contratos Python/JavaScript executados sem chamadas reais à rede. Integração fica em 4.2.
- [x] 3.3 Implementar GET de Registros Clínicos com escopo por Profissional e Paciente e conteúdo liberado; contratos Python/JavaScript executados sem chamadas reais à rede. Integração fica em 4.2.
- [x] 3.4 Implementar retificação append-only, herança de `liberado_paciente` e respostas seguras; contratos Python/JavaScript executados sem chamadas reais à rede. Integração fica em 4.2.

## 4. Testes, documentação e entrega

- [x] 4.1 Atualizar testes Python e JavaScript separados para cada contrato REST GET/POST; verificar ausência de chamadas reais à rede. Testes locais: 71 aprovados e 16 aprovados, incluindo validação de transições e respostas legadas sem Disponibilidade.
- [ ] 4.2 Executar integração opt-in no Xano de teste com Conta de Acesso e dados fictícios, incluindo conflitos concorrentes, rollback, permissões e limpeza segura; registrar evidências sem credenciais e preservar histórico.
- [x] 4.3 Atualizar README e documentação de contratos; executar testes locais e `openspec validate agenda-consultas-registros-clinicos-api --strict`. README esclarece que as rotas não estão publicadas; testes direcionados: 71 Python e 16 JavaScript aprovados, validação estrita da change aprovada e specs principais válidas.
- [x] 4.4 Atualizar o modelo de domínio e a visão geral para refletir que Paciente consulta suas Consultas, mas não agenda nem cancela pelo sistema; a equipe da clínica agenda e Profissional/Administrador/Recepcionista autorizados cancelam.
- [ ] 4.5 Revisar diff e critérios de aceitação, abrir PR vinculado à Issue e solicitar revisão do grupo; verificar ausência de segredos e mudanças fora do escopo.
- [ ] 4.6 Após integração e verificações concluídas, arquivar a change e sincronizar as specs pela CLI; validar as specs principais sem editá-las manualmente.
