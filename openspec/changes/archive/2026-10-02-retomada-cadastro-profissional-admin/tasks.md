## 1. Auditoria local

- [x] 1.1 Confirmar que os exports `GET /especialidades` e `POST /profissionais`, cliente REST, telas e testes por contrato estão versionados; registrar os caminhos encontrados.
- [x] 1.2 Comparar implementação, README e requisitos de `cadastro-profissional` e `acesso-autenticado`; foi encontrada divergência no rótulo da ação de retorno (a spec exige “Voltar”) e ausência da tabela de contratos de cadastro profissional no README. Artefatos arquivados preservados.
- [x] 1.3 Executar testes locais sem rede: `pytest tests/api_contracts tests/test_profissionais.py tests/test_acesso.py tests/test_interface.py -q -p no:cacheprovider` (152 aprovados) e cinco contratos JavaScript de login, identidade, logout, especialidades e cadastro profissional (5 aprovados).

## 2. Testes locais

- [x] 2.1 Executar os testes unitários Python dos contratos, cadastro, autenticação e interface: 152 aprovados; após a correção de rótulo, `tests/test_profissionais.py` passou com 58 aprovados.
- [x] 2.2 Executar os cinco testes unitários JavaScript de login, identidade, logout, especialidades e cadastro de Profissional: 5 aprovados. Nenhum teste envia requisições reais.
- [x] 2.3 Corrigir a divergência reproduzida no rótulo da ação de retorno: o formulário agora exibe “Voltar”, conforme requisito; repetir os testes de Profissional resultou em 58 aprovações.

## 3. Fechamento

- [x] 3.1 Atualizar README com os contratos, comandos, resultados dos testes unitários e a limitação de que eles não comprovam o Xano publicado.
- [x] 3.2 Revisar o diff desta retomada e validar o OpenSpec; manter a branch `feat/3-retomada-cadastro-profissional` para a Issue #3. Não abrir PR até novo pedido do usuário, que pretende acrescentar outros itens à branch.
