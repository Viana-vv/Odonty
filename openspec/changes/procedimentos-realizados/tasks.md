## 1. Contrato e modelo Xano

- [x] 1.1 Atualizar `consulta_procedimento` com situação `planejado` e campos opcionais separados para Profissional/data de realização, preservando os campos atuais de planejamento.
- [x] 1.2 Criar GET autenticado que lista somente Procedimentos da Consulta do Profissional autenticado, incluindo situação e dados de planejamento/realização.
- [x] 1.3 Criar PATCH atômico limitado a `planejado` → `realizado`, atribuindo Profissional autenticado e horário do servidor; retornar erros seguros para escopo inválido, estado repetido e vínculo inexistente.
- [ ] 1.4 Validar a migration e rotas em grupo Xano temporário, confirmar valores padrão nos vínculos legados e respeitar intervalo mínimo de três segundos entre chamadas; interromper se não for seguro.

## 2. Cliente e tela

- [x] 2.1 Criar módulo dedicado de cliente REST para os dois contratos, com endpoint via configuração de ambiente e tratamento de autenticação, autorização, falha e resposta inválida.
- [x] 2.2 Criar página Streamlit independente no estilo Sorriso Mais, listando situação, autoria/data da realização e ação apenas para itens planejados.
- [x] 2.3 Documentar a interface pública do módulo para integração posterior da navegação por outro agente, sem alterar os arquivos reservados.

## 3. Verificação

- [x] 3.1 Criar teste unitário Python e JavaScript separados para o GET, sem rede real.
- [x] 3.2 Criar teste unitário Python e JavaScript separados para o PATCH, sem rede real.
- [x] 3.3 Criar testes de tela para lista vazia, transição bem-sucedida, erro de API, sessão expirada e ausência da ação em itens realizados.
- [x] 3.4 Executar os testes relevantes e validar os artefatos OpenSpec; revisar diff e confirmar ausência de credenciais e dados reais.
