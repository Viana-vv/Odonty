## 1. Tela conectada

- [x] 1.1 Criar módulo isolado de listagem que obtenha opções pela rota autorizada existente e apresente somente ID e nome; verificado por teste sem rede que o cliente existente é chamado com a sessão e apenas `pacientes` é renderizado.
- [x] 1.2 Implementar busca por nome e estados de carregamento, falha e lista vazia com a referência visual aprovada; verificado por testes da interface sem rede.

## 2. Verificação e revisão

- [x] 2.1 Criar testes de UI para sucesso, filtro, vazio, erro e autorização recusada usando cliente simulado; verificado com 8 testes próprios e sem requisições reais.
- [x] 2.2 Adicionar testes de navegação/regressão para módulos conectados, áreas indisponíveis e proteção por perfil; verificado em testes Streamlit sem rede.

## 3. Roteamento e atalhos

- [x] 3.1 Implementar mapa de módulos e despacho de áreas conectadas disponíveis, protegendo acesso direto por perfil e preservando o modo de demonstração; verificado com módulos simulados e regressão do menu.
- [x] 3.2 Oferecer atalhos condicionais para Nova Consulta na Visão geral e Agenda, preservando o formulário atual da Agenda; verificado para Administrador, Recepcionista, Profissional e módulo ausente.

## 4. Verificação final

- [x] 4.1 Executar testes pertinentes, validar OpenSpec e revisar diff integral para confirmar escopo, privacidade, ausência de `.pyc`/`.venv` e compatibilidade visual; verificado com 42 testes Python, teste JavaScript do contrato, `openspec validate --strict` e diff staged seletivo.
