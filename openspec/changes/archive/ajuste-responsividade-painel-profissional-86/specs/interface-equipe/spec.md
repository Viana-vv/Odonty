## MODIFIED Requirements

### Requirement: Layout responsivo e acessível
As telas SHALL permanecer legíveis e utilizáveis em computador, tablet, celular e teclado, com controles alcançáveis, foco visível e formulário sem rolagem horizontal. Em tablet, o painel do Profissional SHALL organizar a Agenda e os atalhos em sequência vertical quando a composição lado a lado não comportar seus rótulos. Em desktop, SHALL manter a Agenda e os atalhos lado a lado. Em celular, conteúdo e navegação SHALL se reorganizar sem sobreposição ou rolagem horizontal da página.

#### Scenario: Reduzir a largura da tela
- **WHEN** uma tela existente é aberta em tablet ou celular
- **THEN** conteúdo, mascote, campos e ações se reorganizam sem sobreposição nem rolagem horizontal.

#### Scenario: Navegar por teclado
- **WHEN** uma pessoa percorre login ou cadastro usando teclado
- **THEN** a ordem de foco é compreensível e o foco permanece visível em cada controle.

#### Scenario: Usar painel Profissional em tablet
- **WHEN** um Profissional abre a Visão geral em uma viewport de tablet, como 768 px
- **THEN** a Agenda e Acesso rápido aparecem em sequência vertical e o rótulo “Ver agenda completa” fica legível por inteiro.

#### Scenario: Usar painel Profissional em computador
- **WHEN** um Profissional abre a Visão geral em uma viewport desktop, como 1440 px
- **THEN** a Agenda e Acesso rápido permanecem lado a lado, sem comprimir o rótulo do botão.

#### Scenario: Usar painel Profissional em celular
- **WHEN** um Profissional abre a Visão geral em uma viewport de 360 px ou 390 px
- **THEN** métricas, Agenda e atalhos permanecem acessíveis em fluxo vertical sem rolagem horizontal.
