## 1. Preparação e revisão

- [x] 1.1 Criar Issue #3 para a change; verificar vínculo https://github.com/Viana-vv/Odonty/issues/3.
- [x] 1.2 Revisar e aprovar proposal, specs, design e tasks; verificar decisão sobre contrato, campos, senha inicial e escopo exclusivo de Dentista.
- [x] 1.3 Inspecionar metadados do Xano e definir estrutura física compatível; verificar preservação das tabelas/APIs legadas e registrar mapeamento sem segredos.

## 2. Backend Xano

- [x] 2.1 Confirmar vínculo Profissional–Conta de Acesso e unicidade de CRO/e-mail; inspeção read-only do workspace 149129 em 02/10/2026 confirmou FK única `profissional.conta_acesso_id` e índices únicos de CRO/e-mail.
- [x] 2.2 Implementar GET /especialidades e POST /profissionais com autenticação, sessão e autorização administrativa; exports da branch live confirmam auth `conta_acesso`, validação de sessão e perfil Administrador. Testes unitários de contrato Python e JavaScript passaram.
- [ ] 2.2a Verificar no Xano real os resultados 401/403 para perfis e estados não autorizados.
- [x] 2.3 Implementar validações e criação transacional com perfil profissional fixo; o export live mostra validações, perfil fixo, transação e tratamento de duplicidade. A suíte local passou com 262 testes aprovados.
- [ ] 2.3a Verificar no Xano real 201, 400, 409, rollback e concorrência sem registros parciais.
- [x] 2.4 Proteger respostas e histórico de requisições; exports live mostram resposta sem credenciais, `history = false` e `Cache-Control: no-store`.
- [ ] 2.4a Validar no Xano real que logs de chamadas e falhas não incluem senha, hash ou token.

## 3. Interface e integração

- [x] 3.1 Integrar a operação ao cliente REST sem repetição automática; testes unitários simulam sucesso, erros, timeout e respostas inválidas (`tests/test_profissionais.py`).
- [x] 3.2 Implementar página do Administrador e navegação protegida ao cadastro; testes verificam revalidação, perda de perfil e ausência da ação para Dentista/Recepcionista.
- [x] 3.3 Implementar formulário com confirmação de senha, perfil fixo e retorno; testes cobrem campos inválidos, reenvio, limpeza de credenciais, sucesso e erro.
- [x] 3.4 Verificar login do Dentista criado e preservação da sessão administrativa; evidência de login real registrada em 25/09/2026 e testes locais cobrem separação de acesso e regressão de expiração/logout.

## 4. Verificação e entrega

- [x] 4.1 Executar testes unitários locais sem rede: Python, 262 aprovados e 115 ignorados (cenários externos opt-in); JavaScript, 7 aprovados. O CLI não encontrou testes unitários/workflow cadastrados no workspace.
- [ ] 4.1a Executar no Xano real testes com dados fictícios de concorrência, rollback, duplicação, adulteração de perfil e autorização; os testes dependem de Conta de Acesso fictícia autorizada.
- [x] 4.2 Verificar fluxo completo Administrador → cadastro → login Dentista no navegador, em computador/tablet/celular e por teclado.
- [x] 4.3 Atualizar README e documentação de execução/contrato; verificar instruções reproduzíveis e validar `cadastro-profissional`, `acesso-autenticado` e `cadastro-paciente` com `--strict`.
- [ ] 4.4 Revisar diff, publicar PR de implementação ligado à Issue e solicitar revisão; verificar ausência de segredos e mudanças fora de escopo.
- [ ] 4.5 Após conclusão verificada, arquivar e sincronizar pela CLI OpenSpec; verificar todas as tarefas e specs principais sem edição manual.

## Verificação da correção do cadastro — 25/09/2026

- Corrigida no endpoint publicado a ordem dos argumentos das validações de e-mail e CRO. O teste isolado no Xano rejeitava valores válidos antes da correção e passou a aceitá-los com o padrão como entrada do filtro e o texto como argumento.
- A interface restaura nome, e-mail, CRO e especialidade após rejeição, sem restaurar senha ou confirmação.
- 110 testes locais passaram (`tests/test_acesso.py`, `tests/test_interface.py` e `tests/test_profissionais.py`), incluindo rejeição no primeiro envio seguida de correção e sucesso. OpenSpec validado com `--strict`.
- Cadastro real com dados fictícios confirmado no navegador após a publicação. O login da conta criada retornou HTTP 200 pela API e apresentou a identificação de Dentista, sem ação administrativa, no navegador. As verificações restantes da change continuam pendentes; ocorrências de HTTP 429 exigiram espaçar chamadas de teste.
