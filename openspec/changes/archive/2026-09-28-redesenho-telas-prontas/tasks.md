## 1. Recursos visuais compartilhados

- [x] 1.1 Copiar o mascote `1000323602.jpg` para `assets/` sem alterar a imagem e verificar que o app consegue carregá-lo.
- [x] 1.2 Atualizar os estilos compartilhados para aproximar paleta, tipografia, fundos, cartões, botões e foco das referências; incluir regras responsivas para computador, tablet e celular e foco de teclado visível.

## 2. Telas existentes

- [x] 2.1 Adaptar o login à referência `01-login.png`, mantendo e-mail, senha e mensagens reais; a regressão verifica login válido, inválido e retorno ao formulário.
- [x] 2.2 Adaptar o início da equipe à referência `02-visao-geral.png`, exibindo apenas identidade e ações já implementadas por perfil; navegação e permissões existentes passaram na regressão.
- [x] 2.3 Adaptar os formulários de Paciente e Profissional às referências `09-novo-paciente.png` e `10-novo-profissional.png`; campos, validação, envio, erros e estado passaram na regressão.

## 3. Verificação e documentação

- [x] 3.1 Executar a regressão local de acesso, interface, profissionais e pacientes; 199 testes passaram.
- [x] 3.2 Validar visualmente o login em Chromium em 1440, 768 e 390 px; a largura de rolagem correspondeu à janela nos três tamanhos. Em 390 px, a sequência de teclado alcançou e-mail, senha e botão com `:focus-visible` ativo; capturas locais em `test-results/redesenho-login-*.png`.
- [x] 3.3 Atualizar a descrição visual no README e validar a change com `openspec validate redesenho-telas-prontas --strict`.
