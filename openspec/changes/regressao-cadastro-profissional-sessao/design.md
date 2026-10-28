## Contexto

Os testes reproduzem que a seleção do cadastro some durante a edição do formulário. O callback `abrir_cadastro` chama a limpeza geral, que apaga os dados de formulário ao abrir. Além disso, a lista de Especialidades é exibida através de um campo de atualização separado, cujo evento pode iniciar uma nova renderização, e a mensagem de logout está divergente da política vigente.

## Decisões

- A navegação para o cadastro será idempotente: limpar campos apenas ao entrar pela primeira vez, não a cada rerun enquanto o cadastro já está aberto.
- A lista de Especialidades permanecerá no cache de sessão existente, com escopo por token e TTL atual; erros 429 continuam sujeitos ao bloqueio de repetição.
- Campos não secretos devem sobreviver a reruns. Senha e confirmação permanecem efêmeras e são limpas após submissão/saída.
- A mensagem de falha de logout seguirá o prazo de uma hora definido em `openspec/specs/acesso-autenticado`.
- Não serão alterados endpoints, payloads, Xano ou as regras de autorização.

## Riscos e validação

Alterar callbacks de navegação pode reter valores entre visitas indevidas; a entrada inicial e o botão Voltar precisam continuar limpando o formulário. Validar com `tests/test_profissionais.py` e `tests/test_acesso.py`; a validação real no Xano depende de credenciais disponíveis e não deve usar serviço temporário.

## Questões em aberto

Nenhuma.
