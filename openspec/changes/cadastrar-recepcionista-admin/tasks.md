## 1. Contrato e autorização no Xano

- [x] 1.1 Criar o export do endpoint `POST /contas-acesso/recepcionistas` com sessão válida, autorização exclusiva de Administrador, corpo estrito, perfil fixo, situação ativa, normalização do e-mail e respostas seguras; verificar o export por inspeção automatizada do contrato.
- [x] 1.2 Criar `tests/api_contracts/test_contas_acesso_recepcionistas_post.py` sem rede real, cobrindo rota, Bearer token, validações, conflito, resposta mínima e ausência de senha; verificar executando esse arquivo com `pytest`.
- [x] 1.3 Criar `tests/js/api_contracts/contas-acesso-recepcionistas-post.test.mjs` sem rede real, cobrindo autorização no export, corpo estrito, perfil constante e campos de resposta; verificar executando o arquivo com `node --test`.

## 2. Cliente e interface administrativa

- [x] 2.1 Adicionar ao cliente REST o cadastro de Recepcionista com validação de entrada e resposta, sem repetição automática de resultado incerto; verificar com testes unitários de sucesso, dados inválidos, duplicidade e resposta incompatível.
- [x] 2.2 Adicionar a ação exclusiva do Administrador e o modal responsivo com nome, e-mail, senha e confirmação, removendo credenciais do estado e invalidando o cache `contas-acesso` após sucesso; verificar com testes Streamlit de visibilidade por perfil, envio único, limpeza e mensagens seguras.
- [x] 2.3 Atualizar a navegação e os títulos administrativos sem liberar o formulário a Recepcionista, Profissional ou Paciente; verificar com os testes de roteamento e navegação existentes e novos casos de perfil.

## 3. Documentação e regressão

- [x] 3.1 Documentar no README o fluxo administrativo, o contrato `POST /contas-acesso/recepcionistas`, os limites de dados e a forma de teste; verificar que não há credencial nem dado real nos exemplos.
- [x] 3.2 Executar os testes Python do contrato, interface, navegação e cache, os testes JavaScript do novo `POST` e `openspec validate cadastrar-recepcionista-admin --strict`; verificar que todos terminam com sucesso e registrar os comandos executados na entrega.

Verificação local: 63 testes Python e 7 subtestes de contrato, interface,
navegação e cache passaram. Os 53 testes JavaScript de contratos passaram,
e a validação estrita do OpenSpec aprovou a change. A regressão Python
ampliada registrou 831 aprovações, 118 saltos e uma falha em
`test_saida_limpa_dados[falha_revalidacao]`, reproduzida em `origin/main`.
Três módulos de navegador ficaram fora da regressão por falta de Playwright.

Publicação: a rota foi importada na branch `v1` (live) do Xano. O export
remoto confirmou as referências à validação de sessão e à tabela
`conta_acesso`. Um POST sem credenciais retornou HTTP 401. A confirmação de
criação autenticada no ambiente publicado depende de uma sessão fictícia
de Administrador.
