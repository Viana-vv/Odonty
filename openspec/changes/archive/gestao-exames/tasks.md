## 1. Contrato e cliente REST

- [x] 1.1 Definir modelos de entrada, saída e situações permitidas para Exame e verificar cobertura nos testes de contrato.
- [x] 1.2 Implementar cliente REST isolado para GET `/exames`, POST `/exames` e PATCH `/exames/{id}/situacao`, verificando autenticação, erros e ausência de dados de arquivo nos testes Python e JavaScript.

## 2. Backend Xano

- [x] 2.1 Criar a tabela e os endpoints de Exame com vínculo a Paciente, Consulta e Profissional, verificando o script/export em ambiente fictício.
- [x] 2.2 Aplicar autorização por perfil e vínculo clínico no Xano, verificando cenários de paciente próprio, profissional relacionado e acesso negado.
- [x] 2.3 Validar transições sequenciais de situação, histórico append-only, cronologia, resultado obrigatório na liberação e ausência de anexos, verificando respostas de sucesso e erro.

## 3. Tela Streamlit

- [x] 3.1 Implementar a tela de Exames com hierarquia, cores, espaçamento e estados visuais do kit Sorriso Mais, verificando renderização em estados carregando, vazio, sucesso e erro.
- [x] 3.2 Integrar formulário e listagem ao cliente REST sem expor resultado indevido, upload ou URL pública, verificando permissões e mensagens compreensíveis.
- [x] 3.3 Exibir ao Profissional as transições permitidas, os campos de realização/resultado e a ação de atualizar; manter os controles de alteração ocultos para Paciente e permitir retentativa de carregamento.

## 4. Verificação final

- [x] 4.1 Executar testes Python e JavaScript da change, lint/compilação e `openspec validate --strict`, corrigindo falhas antes do commit.
- [x] 4.2 Executar cenários remotos somente em Xano temporário com dados fictícios e intervalo de rate limit. Em 25/10/2026, `pytest tests/test_xano_exames_integracao.py` passou (1 teste, 197,21 s), cobrindo compilação, autenticação, autorização, escopo próprio, transições, cronologia, histórico, resultado obrigatório, respostas HTTP e intervalo mínimo de 4,05 s; grupo, função e tabelas temporários foram removidos sem erro.
- [x] 4.3 Revisar diff, confirmar que não há credenciais/dados reais e criar commit descritivo na branch da atividade.
- [x] 4.4 Verificar por testes locais a transição e liberação de resultado pela tela, conferir os contratos e registrar se a integração real está disponível nesta execução. Suíte completa: 517 passaram, 116 ignorados por gates de integração; testes JavaScript de contratos de Exames: 5 passaram; `openspec validate gestao-exames --type change --strict`: válido. Nesta execução, `XANO_TESTAR_EXAMES` permaneceu desativado; nenhuma chamada real ao Xano foi feita. As rotas presentes nos exports são GET/POST `/exames` e PATCH `/exames/{id}/situacao`; elas não foram revalidadas remotamente nesta execução.
