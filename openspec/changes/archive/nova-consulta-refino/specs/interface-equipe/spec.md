## MODIFIED Requirements

### Requirement: Layout responsivo e acessível
As telas SHALL permanecer legíveis e utilizáveis em computador, tablet, celular e teclado, com controles alcançáveis, foco visível e formulários sem rolagem horizontal. O formulário Nova Consulta SHALL organizar visualmente os campos existentes em uma sequência clara de seleção de Paciente, Data e Profissional, escolha de Horário e Procedimentos, Observações e ações finais, seguindo a referência visual 08 do kit Sorriso Mais. A composição SHALL adaptar-se a telas estreitas sem ocultar ou substituir controles funcionais.

#### Scenario: Reduzir a largura da tela
- **WHEN** uma tela existente é aberta em tablet ou celular
- **THEN** conteúdo, campos e ações se reorganizam sem sobreposição nem rolagem horizontal.

#### Scenario: Navegar por teclado
- **WHEN** uma pessoa percorre login ou cadastro usando teclado
- **THEN** a ordem de foco é compreensível e o foco permanece visível em cada controle.

#### Scenario: Preencher Nova Consulta em tela larga
- **WHEN** Administrador ou Recepcionista autorizado abre Nova Consulta em computador
- **THEN** encontra os campos atuais em grupos visuais coerentes com a referência 08 e pode concluir o agendamento pelos controles existentes.

#### Scenario: Preencher Nova Consulta em tela estreita
- **WHEN** Administrador ou Recepcionista autorizado abre Nova Consulta em celular ou tablet estreito
- **THEN** os campos e ações se reorganizam em fluxo legível sem rolagem horizontal nem perda de controles.

#### Scenario: Horário indisponível ou conflito durante o agendamento
- **WHEN** não há horário disponível ou o Xano informa conflito ao enviar a Consulta
- **THEN** a interface preserva o estado vazio ou mensagem de conflito existente, sem sugerir que o agendamento foi concluído.

#### Scenario: Perfil sem autorização abre Nova Consulta
- **WHEN** uma Conta de Acesso sem perfil Administrador ou Recepcionista abre a tela
- **THEN** não recebe o formulário nem pode enviar uma Consulta.
