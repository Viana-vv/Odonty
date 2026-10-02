## 1. Revisão dos contratos e compatibilidade

- [x] 1.1 Revisar com o grupo caminhos, métodos, payloads, respostas, estados e matriz de permissões definidos nas specs; proposta aprovada pelo usuário em 02/10/2026 e registrada no design antes de iniciar alterações no Xano.
- [x] 1.2 Confirmar o mapeamento das tabelas legadas sem ler registros reais e definir migração aditiva; pull read-only do workspace 149129 confirmou `consulta` sem vínculo com Disponibilidade e com um único `procedimento_id`, além das estruturas legadas de Prontuário. Nenhum registro foi lido; o design preserva as tabelas e relações antigas sem conversão ou exclusão.

## 2. Disponibilidades e Consultas no Xano

- [ ] 2.1 Criar a estrutura de Disponibilidade da Agenda e vínculos necessários para Consultas e múltiplos Procedimentos; verificar referências e compatibilidade preservando os campos legados.
- [ ] 2.2 Implementar consulta REST de disponibilidades com filtros e escopo de acesso; testar horários passados, bloqueados, reservados e Profissionais inativos sem rede em unit tests.
- [ ] 2.3 Implementar criação/alteração de disponibilidade com autorização no Xano e validação de intervalos; testar sobreposição, limites inválidos, sessão ausente e perfis sem permissão.
- [ ] 2.4 Implementar agendamento atômico de Consulta e reserva da Disponibilidade; testar vínculos inconsistentes, conflito por Profissional/Paciente, concorrência e rollback em branch de teste.
- [ ] 2.5 Implementar listagens e atualizações de situação de Consulta por perfil; testar escopo, transições inválidas, cancelamento e preservação do histórico.

## 3. Registros Clínicos

- [ ] 3.1 Criar estrutura separada para Registro Clínico e vínculos com Prontuário, Paciente, Profissional e Consulta; testar integridade referencial sem alterar tabelas legadas.
- [ ] 3.2 Implementar criação de Registro Clínico autorizada pelo Xano; testar sucesso, campos obrigatórios, vínculos de Paciente/Consulta incompatíveis, sessão inválida e perfil administrativo.
- [ ] 3.3 Implementar consulta de Registros Clínicos com escopo por Profissional e Paciente e conteúdo liberado; testar acesso próprio, acesso alheio, Recepcionista e Administrador.
- [ ] 3.4 Implementar retificação sem sobrescrever histórico e proteção de respostas/logs; testar autoria, justificativa, histórico anterior e ausência de conteúdo clínico em erros.

## 4. Testes, documentação e entrega

- [x] 4.1 Criar testes unitários Python e JavaScript separados por cada contrato REST GET/POST; verificar ausência de chamadas reais à rede nessas suítes. Cobertura local adicionada para sete contratos GET/POST, com requests simuladas em Python e checagens estáticas do cliente em JavaScript; não valida endpoints publicados no Xano.
- [ ] 4.2 Executar integração opt-in no Xano de teste com Conta de Acesso e dados fictícios, incluindo conflitos concorrentes, rollback, permissões e limpeza segura; registrar evidências sem credenciais e preservar histórico.
- [x] 4.3 Atualizar README e documentação de contratos; executar testes locais e `openspec validate agenda-consultas-registros-clinicos-api --strict`. README esclarece que as rotas não estão publicadas nem validadas; testes: 278 aprovados, 115 ignorados, 14 testes JavaScript aprovados, validação estrita da change aprovada e specs principais válidas.
- [ ] 4.4 Revisar diff e critérios de aceitação, abrir PR vinculado à Issue e solicitar revisão do grupo; verificar ausência de segredos e mudanças fora do escopo.
- [ ] 4.5 Após integração e verificações concluídas, arquivar a change e sincronizar as specs pela CLI; validar as specs principais sem editá-las manualmente.
