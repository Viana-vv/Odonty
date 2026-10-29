## 1. Contrato e Xano

- [x] 1.1 Adicionar teste Python por rota GET comprovando retificações e metadados retornados, sem rede real.
- [x] 1.2 Adicionar teste JavaScript do contrato GET comprovando isolamento, ordenação e ausência de conteúdo em logs.
- [x] 1.3 Alterar export GET para buscar retificações somente dos registros autorizados; validar sintaxe e escopo por teste do export.
- [x] 1.4 Revalidar/criar testes Python e JavaScript por cada POST existente (registro e retificação), cobrindo campos inválidos e autorização no export.

## 2. Interface e verificação

- [x] 2.1 Renderizar trilha append-only abaixo do conteúdo original usando os campos retornados pelo Xano; validar com AppTest.
- [x] 2.2 Executar testes Python e JavaScript dos três contratos GET/POST e AppTest do Prontuário sem chamadas de rede reais.
- [ ] 2.3 Validar integração no Xano publicado com contas fictícias de Profissional, Paciente e Recepcionista, incluindo histórico e retificação. Pendente: não há credenciais clínicas fictícias autenticadas configuradas; o token de Metadata API não substitui a Conta de Acesso da aplicação.
- [x] 2.4 Atualizar README com status real da publicação e resultado verificável; não declarar Xano validado sem integração real.
- [x] 2.5 Impedir que o GET carregue retificações para Paciente quando o Registro Clínico não estiver liberado; cobrir a autorização com testes Python e JavaScript.

## 3. Finalização dos estados de Prontuário e Nova Evolução

- [x] 3.1 Reproduzir com AppTest a troca de Paciente, o contexto do Prontuário selecionado, o cancelamento e a sessão expirada durante a gravação.
- [x] 3.2 Corrigir as seleções dependentes e limpar o rascunho ao cancelar, salvar ou encerrar a sessão; preservar o texto em falhas recuperáveis e impedir a apresentação do histórico após HTTP 401.
- [x] 3.3 Executar os testes locais de interface, sessão e contratos Python/JavaScript, validar a change e registrar resultados e limites da validação real.

## Evidências da finalização local — 29/10/2026

- TDD: cinco cenários falharam antes da correção dos estados; um teste adicional comprovou que limpar apenas o estado não removia o campo clínico da tela após HTTP 401. Todos passaram após as correções.
- `python -B -m pytest tests/test_pagina_prontuario_xano.py tests/test_pagina_nova_evolucao_xano.py tests/test_acesso.py tests/test_interface.py tests/test_cache_xano.py tests/test_roteamento_equipe_xano.py tests/api_contracts -q -p no:cacheprovider --tb=short`: **286 passed, 7 subtests passed**, em 19,51 segundos.
- `node --test tests/js/api_contracts/registros-clinicos-get.test.mjs tests/js/api_contracts/registros-clinicos-post.test.mjs tests/js/api_contracts/retificacoes-post.test.mjs`: **7 passed**.
- `openspec validate prontuario-registros-clinicos-xano --strict`: change válida.
- Nenhuma requisição real ao Xano nesta finalização. A tarefa 2.3 permanece pendente e bloqueia a aprovação final e o archive; a existência de configuração administrativa não comprova permissões dos perfis clínicos.
- A inspeção visual em navegador/dispositivo não foi executada; verificar diretamente a apresentação do formulário e do histórico em computador e celular. Essa ação manual não é uma tarefa OpenSpec.
