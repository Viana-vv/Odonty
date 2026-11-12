## MODIFIED Requirements

### Requirement: Falha da API apresentada com segurança
A interface SHALL manter os valores editados após falha corrigível e SHALL apresentar mensagem compreensível conforme o erro, incluindo as orientações específicas de validação cadastral quando disponíveis, sem exibir resposta técnica, credenciais ou dados pessoais.

#### Scenario: Serviço indisponível durante a edição
- **WHEN** a API retorna falha de serviço ou resposta incompatível
- **THEN** a interface mantém o formulário preenchido e apresenta orientação segura sem indicar sucesso

#### Scenario: Validação cadastral corrigível
- **WHEN** a API rejeita nome, nascimento, CPF, telefone, celular ou e-mail inválido
- **THEN** a interface apresenta o campo ou dado que precisa ser corrigido, mantém os demais valores e não indica sucesso
