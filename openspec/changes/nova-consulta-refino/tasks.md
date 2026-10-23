## 1. Refinamento da tela

- [x] 1.1 Reagrupar visualmente os controles existentes em `sorrisomais/pagina_nova_consulta_xano.py`, preservando os contratos e estados atuais; verificar sequência dos campos e ações no AppTest.
- [x] 1.2 Atualizar testes da tela para garantir perfis, validação, vazio, falha e conflito ainda funcionam sem rede; executar `python -m pytest tests/test_pagina_nova_consulta_xano.py`.

## 2. Verificação dos contratos existentes

- [x] 2.1 Verificar os testes Python separados das rotas GET `/agenda/opcoes`, GET `/disponibilidades` e POST `/consultas`; executar os três arquivos `tests/api_contracts/test_*` correspondentes.
- [x] 2.2 Verificar os testes JavaScript separados das mesmas rotas sem rede; executar `node --test tests/js/api_contracts/agenda-opcoes-get.test.mjs tests/js/api_contracts/disponibilidades-get.test.mjs tests/js/api_contracts/consultas-post.test.mjs`.
- [x] 2.3 Validar artefatos com `openspec validate nova-consulta-refino --strict`; navegador visual indisponível nesta execução, portanto a inspeção manual responsiva em computador e celular permanece pendente.
