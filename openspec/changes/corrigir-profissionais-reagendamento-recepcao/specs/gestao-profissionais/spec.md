## ADDED Requirements

### Requirement: Cadastro incompleto não bloqueia a listagem
O sistema SHALL apresentar registros de Profissional com nome ou CRO vazio ou especialidade ausente como cadastros incompletos, sem inventar dados e sem impedir exibição dos demais. A autorização e as ações de situação por perfil SHALL permanecer vigentes. Respostas com tipos ou identificadores inválidos SHALL continuar rejeitadas.

#### Scenario: Recepcionista consulta cadastro legado incompleto
- **WHEN** GET `/profissionais` contém um cadastro sem nome, CRO e especialidade
- **THEN** a tela apresenta o identificador, campos não informados e aviso de cadastro incompleto junto dos demais Profissionais, sem mensagem de falha de conexão

#### Scenario: Vínculo de especialidade ausente
- **WHEN** a Especialidade do Profissional não existe
- **THEN** o Xano retorna especialidade nula sem interromper a consulta

#### Scenario: Resposta malformada
- **WHEN** a API retorna identificadores duplicados, tipos inesperados ou situação desconhecida
- **THEN** o cliente recusa a resposta e não apresenta dados inválidos como cadastros válidos
