## 1. Preparação e revisão

- [x] 1.1 Criar Issue #3 para a change; verificar vínculo https://github.com/Viana-vv/Odonty/issues/3.
- [x] 1.2 Revisar e aprovar proposal, specs, design e tasks; verificar decisão sobre contrato, campos, senha inicial e escopo exclusivo de Dentista.
- [x] 1.3 Inspecionar metadados do Xano e definir estrutura física compatível; verificar preservação das tabelas/APIs legadas e registrar mapeamento sem segredos.

## 2. Backend Xano

- [ ] 2.1 Preparar vínculo Profissional–Conta de Acesso e unicidade de CRO/e-mail; verificar índices e transformação de senha em contas fictícias.
- [ ] 2.2 Implementar GET /especialidades e POST /profissionais com autenticação, sessão e autorização administrativa atuais; verificar 401/403 para todos os perfis e estados não autorizados.
- [ ] 2.3 Implementar validações e criação transacional com perfil profissional fixo; verificar 201, 400, 409, rollback e concorrência sem registros parciais.
- [ ] 2.4 Proteger respostas e histórico de requisições; verificar ausência de senha, hash e token em respostas e logs, inclusive falhas.

## 3. Interface e integração

- [ ] 3.1 Integrar a operação ao cliente REST sem repetição automática; testar sucesso, erros, timeout e respostas inválidas com simulação.
- [ ] 3.2 Implementar página do Administrador e navegação protegida ao cadastro; verificar revalidação, perda de perfil e ausência da ação para Dentista/Recepcionista.
- [ ] 3.3 Implementar formulário com confirmação de senha, perfil fixo e retorno; verificar campos inválidos, duplo envio, limpeza de credenciais, sucesso e erro.
- [ ] 3.4 Verificar login do Dentista criado e preservação da sessão administrativa; confirmar separação do acesso de Paciente e regressão de expiração/logout.

## 4. Verificação e entrega

- [ ] 4.1 Executar testes locais e no Xano real com dados fictícios, incluindo concorrência, rollback, duplicação, adulteração de perfil e autorização; registrar resultados separados e preservar históricos na limpeza.
- [ ] 4.2 Verificar fluxo completo Administrador → cadastro → login Dentista no navegador, em computador/tablet/celular e por teclado; registrar evidências sem credenciais.
- [ ] 4.3 Atualizar README e documentação de execução/contrato; verificar instruções reproduzíveis e validar OpenSpec estritamente.
- [ ] 4.4 Revisar diff, publicar PR de implementação ligado à Issue e solicitar revisão; verificar ausência de segredos e mudanças fora de escopo.
- [ ] 4.5 Após conclusão verificada, arquivar e sincronizar pela CLI OpenSpec; verificar todas as tarefas e specs principais sem edição manual.

## Verificação da correção do cadastro — 25/09/2026

- Corrigida no endpoint publicado a ordem dos argumentos das validações de e-mail e CRO. O teste isolado no Xano rejeitava valores válidos antes da correção e passou a aceitá-los com o padrão como entrada do filtro e o texto como argumento.
- A interface restaura nome, e-mail, CRO e especialidade após rejeição, sem restaurar senha ou confirmação.
- 110 testes locais passaram (`tests/test_acesso.py`, `tests/test_interface.py` e `tests/test_profissionais.py`), incluindo rejeição no primeiro envio seguida de correção e sucesso. OpenSpec validado com `--strict`.
- Cadastro real com dados fictícios confirmado no navegador após a publicação. O login da conta criada retornou HTTP 200 pela API e apresentou a identificação de Dentista, sem ação administrativa, no navegador. As verificações restantes da change continuam pendentes; ocorrências de HTTP 429 exigiram espaçar chamadas de teste.
