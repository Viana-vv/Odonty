## 1. Planejamento e proteção

- [x] 1.1 Revisar AGENTS.md, visão do projeto, modelo de domínio, README e changes de Exames, Procedimentos realizados e Reagendamento.
- [x] 1.2 Conferir presença de configurações sem revelar valores; usar exclusivamente grupos temporários novos, com plano creation-only, sem publicar nem alterar produção.

## 2. Verificação

- [x] 2.1 Executar smoke remoto opt-in dos três contratos em grupos temporários, com dados fictícios e limpeza confirmada. Exames: `pytest tests/test_xano_exames_integracao.py` passou (1 teste, 231,06 s); Procedimentos: `pytest tests/test_xano_procedimentos_integracao.py` passou (1 teste, 249,76 s). Ambos os harnesses limitam chamadas a uma por pelo menos 4,05 s, confirmam limpeza no teardown e não escrevem no grupo principal. Reagendamento: dry-run planejou somente criações; `python tests/integration/verificar_reagendamento_xano.py executar` passou com 74 requisições e intervalo mínimo de 3,203 s (máximo de 7 em qualquer janela de 20 s), validando 401/403, 400/404/409, sucesso administrativo, rollback integral induzido e quatro concorrências 201/409; limpeza confirmou remoção do grupo, 13 tabelas e função. Nenhuma alteração/publicação de produção.
- [x] 2.2 Validações locais sem rede: 30 testes Python de contrato de Reagendamento passaram; 14 testes Python de Exames/Procedimentos passaram; os harnesses opt-in sem ativação foram confirmados como ignorados (2); 12 verificações JavaScript passaram. Resultado: 56 aprovados, 2 ignorados. Um comando exploratório combinado inicialmente falhou por caminho incorreto/colisão de fixtures; reexecutado por suíte e diretório correto, sem alterar código.
- [x] 2.3 Executar `openspec validate smoke-contratos-xano --strict` e `git diff --check`; ambos passaram após ajustar os cabeçalhos ao formato delta OpenSpec.
- [x] 2.4 Criar commit descritivo somente após concluir as verificações possíveis; não fazer push nem PR.
