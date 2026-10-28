## MODIFIED Requirements

### Requirement: Tratamento de envio e proteção da senha
O sistema SHALL impedir submissões simultâneas pela interface, remover senha e confirmação após processamento ou saída da página, não registrar credenciais e não repetir automaticamente cadastros. Falhas de resultado incerto SHALL NOT ser apresentadas como sucesso. Reruns causados por edição de campos SHALL preservar a tela e os valores não secretos, e SHALL reutilizar a lista de Especialidades válida por até cinco minutos na sessão autenticada.

#### Scenario: Sucesso na interface
- **WHEN** o backend confirma a criação
- **THEN** a interface informa sucesso, limpa os campos e permite outro cadastro.

#### Scenario: Falha de conexão ou resposta inválida
- **WHEN** a resposta é perdida, vazia ou incompatível
- **THEN** a interface informa que não confirmou o cadastro, remove as senhas e reabilita o formulário sem repetir a requisição.

#### Scenario: Duplo clique
- **WHEN** a pessoa aciona Cadastrar novamente durante o processamento
- **THEN** a interface mantém apenas um envio em andamento.

#### Scenario: Logs e erros
- **WHEN** ocorre sucesso ou erro durante o cadastro
- **THEN** senha, token e corpos sensíveis não aparecem em logs, respostas ou mensagens técnicas.

#### Scenario: Edição com formulário aberto
- **WHEN** o Administrador altera um campo do formulário antes do envio
- **THEN** a tela continua no cadastro, preserva os valores não secretos e reutiliza as Especialidades em cache.
