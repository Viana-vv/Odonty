## Contexto

Os testes reproduzem que a seleÃ§Ã£o do cadastro some durante a ediÃ§Ã£o do formulÃ¡rio. O callback `abrir_cadastro` chama a limpeza geral, que apaga os dados de formulÃ¡rio ao abrir. AlÃ©m disso, a lista de Especialidades Ã© exibida atravÃ©s de um campo de atualizaÃ§Ã£o separado, cujo evento pode iniciar uma nova renderizaÃ§Ã£o, e a mensagem de logout estÃ¡ divergente da polÃ­tica vigente.

## DecisÃµes

- A navegaÃ§Ã£o para o cadastro serÃ¡ idempotente: limpar campos apenas ao entrar pela primeira vez, nÃ£o a cada rerun enquanto o cadastro jÃ¡ estÃ¡ aberto.
- A lista de Especialidades permanecerÃ¡ no cache de sessÃ£o existente, com escopo por token e sem expiração automática. A atualização manual solicita nova leitura; após erro 429, novas tentativas ficam bloqueadas por 20 segundos. Esse bloqueio não invalida uma lista válida já armazenada; erros 429 continuam sujeitos ao bloqueio de repetiÃ§Ã£o.
- Campos nÃ£o secretos devem sobreviver a reruns. Senha e confirmaÃ§Ã£o permanecem efÃªmeras e sÃ£o limpas apÃ³s submissÃ£o/saÃ­da.
- A mensagem de falha de logout seguirÃ¡ o prazo de uma hora definido em `openspec/specs/acesso-autenticado`.
- NÃ£o serÃ£o alterados endpoints, payloads, Xano ou as regras de autorizaÃ§Ã£o.

## Riscos e validaÃ§Ã£o

Alterar callbacks de navegaÃ§Ã£o pode reter valores entre visitas indevidas; a entrada inicial e o botÃ£o Voltar precisam continuar limpando o formulÃ¡rio. Validar com `tests/test_profissionais.py` e `tests/test_acesso.py`; a validaÃ§Ã£o real no Xano depende de credenciais disponÃ­veis e nÃ£o deve usar serviÃ§o temporÃ¡rio.

## QuestÃµes em aberto

Nenhuma.
