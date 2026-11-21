## 1. Contrato e autorização no Xano

- [ ] 1.1 Criar o export do endpoint `POST /contas-acesso/recepcionistas` com sessão válida, autorização exclusiva de Administrador, corpo estrito, perfil fixo, situação ativa, normalização do e-mail e respostas seguras; verificar o export por inspeção automatizada do contrato.
- [ ] 1.2 Criar `tests/api_contracts/test_contas_acesso_recepcionistas_post.py` sem rede real, cobrindo rota, Bearer token, validações, conflito, resposta mínima e ausência de senha; verificar executando esse arquivo com `pytest`.
- [ ] 1.3 Criar `tests/js/api_contracts/contas-acesso-recepcionistas-post.test.mjs` sem rede real, cobrindo autorização no export, corpo estrito, perfil constante e campos de resposta; verificar executando o arquivo com `node --test`.

## 2. Cliente e interface administrativa

- [ ] 2.1 Adicionar ao cliente REST o cadastro de Recepcionista com validação de entrada e resposta, sem repetição automática de resultado incerto; verificar com testes unitários de sucesso, dados inválidos, duplicidade e resposta incompatível.
- [ ] 2.2 Adicionar a ação exclusiva do Administrador e o modal responsivo com nome, e-mail, senha e confirmação, removendo credenciais do estado e invalidando o cache `contas-acesso` após sucesso; verificar com testes Streamlit de visibilidade por perfil, envio único, limpeza e mensagens seguras.
- [ ] 2.3 Atualizar a navegação e os títulos administrativos sem liberar o formulário a Recepcionista, Profissional ou Paciente; verificar com os testes de roteamento e navegação existentes e novos casos de perfil.

## 3. Documentação e regressão

- [ ] 3.1 Documentar no README o fluxo administrativo, o contrato `POST /contas-acesso/recepcionistas`, os limites de dados e a forma de teste; verificar que não há credencial nem dado real nos exemplos.
- [ ] 3.2 Executar os testes Python do contrato, interface, navegação e cache, os testes JavaScript do novo `POST` e `openspec validate cadastrar-recepcionista-admin --strict`; verificar que todos terminam com sucesso e registrar os comandos executados na entrega.
