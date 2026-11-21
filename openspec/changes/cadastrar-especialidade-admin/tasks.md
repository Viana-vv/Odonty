## 1. Modelo e contrato no Xano

- [ ] 1.1 Auditar os registros fictícios de Especialidade por nome normalizado, definir o registro canônico de eventuais colisões e documentar o resultado sem apagar referências; verificar que nenhuma colisão pendente impede a restrição única.
- [ ] 1.2 Adicionar `nome_normalizado` obrigatório e índice único ao modelo de Especialidade, com preenchimento dos registros existentes e preservação do nome de exibição; verificar o export da tabela e o procedimento de migração por inspeção automatizada.
- [ ] 1.3 Criar o export do endpoint `POST /especialidades` com sessão válida, autorização exclusiva de Administrador, corpo estrito, normalização, criação ativa e respostas seguras; verificar o export por inspeção automatizada do contrato.
- [ ] 1.4 Criar `tests/api_contracts/test_especialidades_post.py` sem rede real, cobrindo rota, Bearer token, validação, normalização, conflito e resposta mínima; verificar executando esse arquivo com `pytest`.
- [ ] 1.5 Criar `tests/js/api_contracts/especialidades-post.test.mjs` sem rede real, cobrindo autorização no export, corpo estrito, chave normalizada, índice único e campos de resposta; verificar executando o arquivo com `node --test`.

## 2. Cliente e interface administrativa

- [ ] 2.1 Adicionar ao cliente REST o cadastro de Especialidade com validação de entrada e resposta, sem repetição automática de resultado incerto; verificar com testes unitários de sucesso, nome inválido, duplicidade e resposta incompatível.
- [ ] 2.2 Adicionar a ação exclusiva do Administrador e o modal responsivo com nome da Especialidade, bloqueio de envio simultâneo e mensagens seguras; verificar com testes Streamlit de visibilidade por perfil, validação, sucesso e falhas.
- [ ] 2.3 Invalidar o cache `especialidades` somente após sucesso confirmado e manter a atualização do cadastro de Profissional sem repetir o `POST`; verificar com teste que a próxima leitura usa `GET /especialidades` e apresenta a nova opção.
- [ ] 2.4 Atualizar a navegação e os títulos administrativos sem liberar o formulário a Recepcionista, Profissional ou Paciente; verificar com os testes de roteamento e navegação existentes e novos casos de perfil.

## 3. Documentação e regressão

- [ ] 3.1 Documentar no README o fluxo administrativo, o contrato `POST /especialidades`, a normalização e o procedimento seguro de migração; verificar que os exemplos usam somente dados fictícios.
- [ ] 3.2 Executar os testes Python dos contratos `GET` e `POST`, interface, cadastro de Profissional, navegação e cache, os testes JavaScript correspondentes e `openspec validate cadastrar-especialidade-admin --strict`; verificar que todos terminam com sucesso e registrar os comandos executados na entrega.
