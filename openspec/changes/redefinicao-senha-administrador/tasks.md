# Tarefas — somente após aprovação

O grupo aprovou as políticas documentadas em07/11/2026 e autorizou somente a primeira entrega local (seção7), na Issue#131 e branch `feat/131-contratos-redefinicao-senha`. Itens1–6 continuam pendentes quando exigem handlers/integração Xano, transporte real ou frontend; evidências parciais da referência offline não os concluem. Dependências operacionais e verificações manuais serão tratadas na conversa, não como tarefas deste checklist. Todos os testes unitários Python/JavaScript abaixo usam rede substituída, relógios controlados e dados fictícios.

## 1. Reconciliar o estado real e provar coordenação

- [ ] 1.1 Versionar seletivamente os schemas/rotas OTP e helpers pertinentes após conciliar com o responsável, preservando GUIDs e contratos; verificar diff contra metadados remotos e inventário de consumidores, sem importar workspace inteiro ou valores de ambiente.
- [ ] 1.2 Especificar no export o mecanismo real de bloqueio/compare-and-swap por conta e ordem de aquisição de cotas, e criar prova automatizada isolada das invariantes; verificar que duas transações sobre a mesma geração não concluem ambas. Testes sem rede não devem ser apresentados como prova do mecanismo remoto; execução isolada real depende de autorização específica posterior.
- [ ] 1.3 Documentar em português a compatibilidade OTP/link, mapeamento de versão de credencial e corte das operações antigas; verificar que o plano preserva contratos externos e não deixa troca OTP sem coordenação/revogação. Interromper se a primitiva ou o escopo compartilhado não atender ao desenho aprovado.

## 2. Estruturas e sessão compatíveis

- [ ] 2.1 Criar exports aditivos de operação de redefinição, versão de credencial, limites e auditoria restrita; testar unicidade, cotas concorrentes, eventos terminais, datas/deadline do servidor e retenção mínima até consultavel_ate, permitindo eliminar segredo/hash antes dos metadados de deduplicação.
- [ ] 2.2 Integrar versão de credencial à emissão/validação de sessão e preservar compatibilidade controlada com sessões legadas; verificar login concorrente com troca, token antigo rejeitado e login novo permitido, sem alterar o prazo normal de sessão.
- [ ] 2.3 Integrar emissão, validação e troca OTP somente ao vínculo conta/versão, consumo/invalidação cruzada e revogação comum aprovados; criar testes Python e JavaScript sem rede em arquivos separados por cada uma das três rotas POST existentes, preservando entradas/saídas, formato, TTL e etapas do OTP, além de verificar concorrência, rollback e revogação global.
- [ ] 2.4 Atualizar documentação técnica de sessão/OTP sem sincronizar automaticamente o conflito uma/oito horas; verificar que descreve a compatibilidade e a diferença entre logout individual e revogação global.

## 3. Solicitação administrativa e transporte

- [ ] 3.1 Implementar adaptador dedicado sem histórico sensível e com orçamento total real validado/persistido; testar HTTP202, recusa inequívoca, resposta incompatível, conexão incerta, morte antes da chamada, deadline exato e resposta tardia, sem iniciar chamada fora do orçamento nem repetir envio. Documentar a primitiva de timeout usada e bloquear ativação se não limitar a duração total.
- [ ] 3.2 Implementar export e cliente de `POST /contas-acesso/{conta_id}/redefinicoes-senha`; criar `tests/api_contracts/test_contas_acesso_redefinicoes_senha_post.py` e `tests/js/api_contracts/contas-acesso-redefinicoes-senha-post.test.mjs`, separados e sem rede, cobrindo autorização, perda de perfil/sessão, conta inexistente/inativa/bloqueada, própria conta, flags divergentes, campos extras e todos os códigos/status propostos.
- [ ] 3.3 Nos testes do POST de criação, cobrir UUIDv7 canônico, variante/versão inválida, fronteiras de idade5min/futuro60s, relógio cliente incorreto, replay conhecido sem frescor e sem nova cota/envio, identidade incompatível, retenção30d e repetição antiga após remoção retornando409. Verificar que timestamps cliente não alteram prazo do token, nova intenção exige ID novo e erro pré-reserva não invalida anteriores.
- [ ] 3.4 Implementar export/cliente de `GET /contas-acesso/{conta_id}/redefinicoes-senha/{operacao_id}`; criar `tests/api_contracts/test_contas_acesso_redefinicao_senha_get.py` e `tests/js/api_contracts/contas-acesso-redefinicao-senha-get.test.mjs`, separados e sem rede, para200,404 indistinto,401,403,400 e503; provar ausência de escrita, criação, hash/token novo, cotas e envio inclusive para UUID desconhecido e flag desligada.
- [ ] 3.5 Testar em ambos os contratos administrativos a projeção exata das datas e dos dois estados, fronteira consultavel_ate, consumo antes da expiração, substituição/invalidação, falha e deadline sem conclusão, além de aceite/recusa tardios sem reativação do link. Documentar tabela de transições e nunca converter aceito em entregue.
- [ ] 3.6 Documentar os três contratos, janela de retenção, flags por ambiente e orçamento de transporte; verificar exemplos fictícios, respostas sem token/link e todos os códigos coerentes entre cliente e export. Flags devem iniciar desligadas e configuração inválida deve impedir novas reservas.

## 4. Confirmação pública e consistência

- [ ] 4.1 Implementar export/cliente de `POST /auth/redefinicoes-senha/confirmar` com política, limite de corpo/código, hash e mensagens genéricas; criar `tests/api_contracts/test_auth_redefinicoes_senha_confirmar_post.py` e `tests/js/api_contracts/auth-redefinicoes-senha-confirmar-post.test.mjs`, separados e sem rede, cobrindo todos os erros,409 ENVIO_EM_PROCESSAMENTO com Retry-After exato e204 sem sessão.
- [ ] 4.2 Testar ausência, formato inválido, expiração na fronteira, usado, substituído, e-mail/versão alterados, conta bloqueada/inativa após emissão, senha fora da política e preservação de espaços; verificar que falhas não trocam senha nem consomem token indevidamente.
- [ ] 4.3 Testar transação/rollback, consumo duplo, OTP versus link, nova solicitação versus confirmação, login concorrente e status tardio do provedor; verificar no máximo uma troca efetiva por geração e nenhuma sessão da senha antiga autorizada após commit.
- [ ] 4.4 Implementar limitação pública por hash e proteção de ingresso compatível com origem confiável, sem confiar em cabeçalhos arbitrários; testar isolamento entre códigos, excesso, erro sanitizado, respostas sem cache e ausência de invalidação de token alheio.
- [ ] 4.5 Documentar condições de ativação/rollback, sem restauração de senha antiga, revivificação de token ou decremento da versão; verificar coerência com os testes de consistência.
- [ ] 4.6 Nos testes Python/JavaScript do POST de confirmação, simular commit concluído com resposta204 perdida; verificar nenhuma repetição automática, token consumido devolvendo400 genérico na tentativa explícita posterior e preservação de senha/revogações já efetivadas. Testar também409 antes do deadline e confirmação após deadline desconhecido, sem reenviar mensagem.

## 5. Interface existente e entrada pelo link

- [ ] 5.1 Registrar Contas de Acesso no menu/roteador existente, preservando consulta por Administrador/Recepcionista; verificar testes de navegação e regressão Python/JavaScript separados do GET `/contas-acesso`, inclusive acesso direto indevido e perda de sessão.
- [ ] 5.2 Implementar flag pública local por ambiente seguindo Configuracao.do_ambiente sem exceção global; verificar por AppTest leitura/carregamento, ausência,0/1/false/true, valor inválido, erro local e divergência remota503, mantendo login/menu/lista/atualização e impedindo envio para Recepcionista.
- [ ] 5.3 Acrescentar botão e confirmação administrativa mascarada com UUIDv7 estável; testar por AppTest que abrir/cancelar diálogo não reserva nada, confirmar cria uma intenção, clique duplo mantém ID, reenvio exige confirmação nova e timeout nunca provoca POST de consulta ou ID automático.
- [ ] 5.4 Acrescentar consulta explícita por GET na interface; testar carregamento, estados independentes,200/404/erro/401/403, inclusive desconhecido antes da primeira reserva e resultado após consumo/expiração/retenção. Verificar que flag de novos envios desligada preserva GET autorizado e que falha de consulta não é apresentada como falha de envio.
- [ ] 5.5 Criar formulário público antes do gate de login reutilizando a identidade existente; testar por AppTest query ausente/duplicada/desconhecida, captura/limpeza, rerun mantendo modo, aba autenticada, recarga sem estado, confirmação divergente e limpeza de segredos. Testar409/Retry-After com nova ação explícita após espera, sem polling de confirmação.
- [ ] 5.6 Simular por AppTest troca concluída com204 perdido: mensagem de resultado não confirmado, botão login, limpeza de código/senhas/sessão da aba e nenhum segundo POST. Testar400 LINK_INDISPONIVEL para usado com mesma mensagem genérica, sem dado da conta; verificar flag desligada após emissão mantendo confirmação vigente e revogação emergencial impedindo uso.
- [ ] 5.7 Verificar automaticamente que GET/preview não envia e-mail nem consome token, código não vira Credencial e formulário não acessa conteúdo protegido; acrescentar testes de ausência de recursos externos e sanitização de mensagens.
- [ ] 5.8 Atualizar instruções de execução e implantação com flags independentes, desligamento normal versus emergência, URL HTTPS fixa, logs/headers e uso local fictício; verificar que não recomenda localhost externo, idempotência indefinida ou apagamento de histórico por clear().

## 6. Verificação integrada e entrega

- [ ] 6.1 Executar regressão de autenticação/OTP, Contas, navegação e clientes, além dos contratos novos GET/POST e do GET existente de contas, com arquivos Python/JavaScript separados por rota e sem rede; anexar resultados sem apresentar mocks como prova real de atomicidade.
- [ ] 6.2 Preparar suíte automatizada opt-in para concorrência/atomicidade em ambiente isolado, com e-mail substituído por transporte controlado e somente dados fictícios; verificar guarda que impede atingir v1/produção ou enviar mensagens reais sem autorização específica.
- [ ] 6.3 Validar a change com `openspec validate redefinicao-senha-administrador --strict` e revisar diff limitado ao escopo aprovado; entregar evidências e dependências ainda abertas, sem habilitação/publicação implícita.

## 7. Primeira entrega local autorizada — Issue #131

- [x] 7.1 Conferir/preservar branch e trabalho existente, criar Issue e branch específicas; verificar estado Git sem commit ou push.
- [x] 7.2 Confirmar Python3.12.10 sem uuid7 nativo e implementar UUIDv7 com biblioteca padrão, sem mudar Python/dependências do projeto; verificar vetorRFC9562, formato, variante, timestamp e sintaxePython3.10 em testes locais.
- [x] 7.3 Implementar contrato OpenAPI e cliente dos dois POST/GET com validação, erros sanitizados, Retry-After e resultado incerto; verificar89 testes Python novos por rota com transporte substituído e9 testesJavaScript novos.
- [x] 7.4 Acrescentar schemas locais de operação/controle/auditoria e campos de versão de credencial, sem aplicar no Xano; revisar definições e manter explicitamente pendente sua validação e uso pelos handlers reais.
- [x] 7.5 Implementar referência executável offline e testes de autorização, GET sem escrita, estados, retenção/idempotência, cotas, concorrência local, rollback e resposta perdida; verificar61 testes do modelo sem declarar prova transacional remota.
- [x] 7.6 Manter configuração desligada por padrão e erro restrito ao recurso; verificar testes de configuração e regressão de acesso/contratos existentes.
- [x] 7.7 Documentar escopo local, resultados, limites e gates remotos em `docs/redefinicao-senha-local.md`; conferir391 testesPython e10JavaScript aprovados, revisão independente e validação estrita OpenSpec.

## Workflow follow-up

- Solicitar revisão de outro integrante e PR somente na etapa autorizada de implementação, preservando trabalho alheio.
- Arquivar e sincronizar deltas somente quando implementação, verificações e aprovação estiverem completas; não editar `openspec/specs/` manualmente.
