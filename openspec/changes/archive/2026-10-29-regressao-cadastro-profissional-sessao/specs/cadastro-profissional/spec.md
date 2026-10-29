## MODIFIED Requirements

### Requirement: Tratamento de envio e proteÃ§Ã£o da senha
O sistema SHALL impedir submissÃµes simultÃ¢neas pela interface, remover senha e confirmaÃ§Ã£o apÃ³s processamento ou saÃ­da da pÃ¡gina, nÃ£o registrar credenciais e nÃ£o repetir automaticamente cadastros. Falhas de resultado incerto SHALL NOT ser apresentadas como sucesso. Reruns causados por ediÃ§Ã£o de campos SHALL preservar a tela e os valores nÃ£o secretos, e SHALL reutilizar a lista de Especialidades vÃ¡lida por atÃ© cinco minutos na sessÃ£o autenticada.

#### Scenario: Sucesso na interface
- **WHEN** o backend confirma a criaÃ§Ã£o
- **THEN** a interface informa sucesso, limpa os campos e permite outro cadastro.

#### Scenario: Falha de conexÃ£o ou resposta invÃ¡lida
- **WHEN** a resposta Ã© perdida, vazia ou incompatÃ­vel
- **THEN** a interface informa que nÃ£o confirmou o cadastro, remove as senhas e reabilita o formulÃ¡rio sem repetir a requisiÃ§Ã£o.

#### Scenario: Duplo clique
- **WHEN** a pessoa aciona Cadastrar novamente durante o processamento
- **THEN** a interface mantÃ©m apenas um envio em andamento.

#### Scenario: Logs e erros
- **WHEN** ocorre sucesso ou erro durante o cadastro
- **THEN** senha, token e corpos sensÃ­veis nÃ£o aparecem em logs, respostas ou mensagens tÃ©cnicas.

#### Scenario: EdiÃ§Ã£o com formulÃ¡rio aberto
- **WHEN** o Administrador altera um campo do formulÃ¡rio antes do envio
- **THEN** a tela continua no cadastro, preserva os valores nÃ£o secretos e reutiliza as Especialidades em cache.


#### Scenario: Limite de requisições de Especialidades
- **WHEN** o Xano retorna 429 ao carregar Especialidades
- **THEN** a interface bloqueia novas tentativas por 20 segundos e mantém qualquer lista válida em cache; após o período, permite nova leitura.

#### Scenario: Atualização manual de Especialidades
- **WHEN** a pessoa solicita atualização manual fora do bloqueio por 429
- **THEN** a interface realiza nova leitura, independentemente do tempo desde que a lista foi armazenada.