## Decisões

- Reutilizar as suítes já existentes: `tests/test_xano_exames_integracao.py`, `tests/test_xano_procedimentos_integracao.py` e `tests/integration/verificar_reagendamento_xano.py`; não duplicar contratos nem criar clientes de rede novos.
- Integrações são opt-in. Não executar mutações remotas se não houver Metadata URL, workspace, token administrativo e confirmação de alvo temporário segregado. A variável `XANO_API_BASE_URL` isolada não autoriza publicação ou gravação no grupo principal.
- Aplicar limitador comum operacional de no máximo 10 requisições por 20 segundos, com intervalo entre cada chamada (as suítes existentes esperam pelo menos 4,05 segundos). Concorrência funcional deve manter essa cadência nos inícios das chamadas.
- Cobrir 401, 403, 400, 404 e 409 conforme aplicável aos contratos. O rollback induzido é obrigatório no Reagendamento; nos contratos cuja operação é transacional, verificar ausência de persistência parcial quando o cenário existe.
- Limpeza pode inativar contas fictícias temporárias e remover somente grupo, tabelas, funções e artefatos identificados como criados por aquela execução. Preservar histórico clínico e dados preexistentes; interromper se a propriedade de um artefato for ambígua.
- Não há promoção, publicação ou alteração automática de produção. Resultados remotos devem registrar data, alvo segregado, contagem/intervalo e resumo de cenários, sem tokens, dados clínicos ou identificadores pessoais.

## Riscos

Sem credenciais de Metadata não é possível verificar a existência do grupo temporário nem executar/limpar os objetos. Nesse caso, registrar bloqueio real, executar apenas testes locais sem rede e deixar a verificação remota pendente; resultados anteriores no README/tasks não contam como execução atual.
