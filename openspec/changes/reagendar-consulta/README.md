# Reagendar Consulta — Issue #64

Implementação local pronta para revisão, sem publicação. A verificação real no Xano permanece pendente e a change não foi arquivada.

## Entrega

- Tabela aditiva `consulta_reagendamento` com origem e destino únicos, responsável, justificativa e data; relações anteriores permanecem intactas.
- `POST /consultas/{id}/reagendamento` cancela a Consulta original, cria a nova, vincula ambas, audita e atualiza as Disponibilidades na mesma transação.
- `PATCH /disponibilidades/{id}` relê e revalida o estado após a trava para rejeitar edição obsoleta concorrente. Essa correção foi autorizada por ser necessária à reserva segura.
- `sorrisomais.reagendamento_consulta.reagendar_consulta(cliente, token, consulta_id, disponibilidade_id, justificativa)` usa o transporte REST comum. Não há cancelamento e criação em duas chamadas.
- `sorrisomais.pagina_reagendar_consulta_xano.renderizar(cliente, conta)` oferece a interface administrativa; a navegação será integrada pelo agente principal. A tela segue o formulário Nova Consulta do kit Sorriso Mais, com seletores funcionais e composição em duas colunas.

## Verificações executadas

```powershell
python -m pytest tests/api_contracts/test_consultas_id_reagendamento_post.py tests/api_contracts/test_disponibilidades_patch.py tests/api_contracts/test_consultas_post.py tests/api_contracts/test_consultas_get.py -q
```

43 testes passaram: 30 para o contrato novo e regressões dos contratos de Consulta e Disponibilidade. HTTP simulado, sem rede. As verificações de transação, travas e releitura analisam a estrutura do export; não comprovam concorrência nem rollback na execução Xano.

```powershell
python -m pytest tests/test_pagina_reagendar_consulta_xano.py tests/test_pagina_nova_consulta_xano.py tests/test_transicoes_consulta.py -q
```

49 testes passaram, sendo 20 AppTests da nova tela. Cobertura de seleção, deduplicação de Consultas, filtros, campos obrigatórios, listas vazias, perfis, sucesso, conflito, falhas, sessão expirada e cancelamento da interface. Os dois grupos Python foram executados separadamente: a mistura de AppTest antes de contratos no mesmo processo afeta a descoberta das fixtures existentes.

```powershell
node --test tests/js/api_contracts/consultas-id-reagendamento-post.test.mjs tests/js/api_contracts/disponibilidades-patch.test.mjs tests/js/api_contracts/consultas-post.test.mjs tests/js/api_contracts/consultas-get.test.mjs
openspec validate reagendar-consulta --strict
git diff --check
```

7 verificações JavaScript passaram; OpenSpec válido e diff sem erros de espaço.

O dry-run do CLI Xano para os dois exports novos mostrou somente criação da tabela e do endpoint. Foi prévia, sem mutação; não foi tratado como prova de compilação/publicação.

## Limitação real e próximos passos

Os dois perfis locais encontrados apontam para o workspace principal 149129; não há grupo/workspace temporário isolado identificado na configuração local. Conforme orientação de coordenação, nenhuma mutação remota, publicação ou chamada à API de produção foi executada. Não foram acessados registros de pacientes. A tarefa 3.1 continua aberta.

Em 24/10/2026, uma nova tentativa de verificação confirmou o bloqueio por meio de leituras de metadados, respeitando 3,2 segundos entre chamadas. A inspeção também identificou diferença de serialização: o endpoint novo usa `agenda_controle`, enquanto o PATCH local ainda depende de `profissional.agenda_lock_version`, ausente no schema remoto. A compilação e a proteção concorrente não podem ser declaradas verificadas. Detalhes, limites da inspeção e próximos passos estão em [verificacao-xano-2026-10-24.md](verificacao-xano-2026-10-24.md).

Antes de publicar, executar em ambiente temporário isolado: compilação dos exports, sessão ausente/expirada, perfis administrativos e negados, sucesso com vínculo persistente, preservação de relações originais, recursos inválidos, intervalo inválido/passado, destino bloqueado/ocupado, conflitos de Paciente e Profissional, duas reservas concorrentes, dois reagendamentos da mesma Consulta, edição de Disponibilidade aguardando reserva e falha induzida depois da criação para comprovar rollback integral. Usar dados fictícios e aguardar pelo menos três segundos entre chamadas.

A inspeção visual integrada de desktop e celular deve conferir os espaçamentos, os seletores em duas colunas e a reorganização responsiva do formulário; ela depende da integração de navegação pelo principal e deve ser informada diretamente ao grupo, sem tarefa manual no OpenSpec.
