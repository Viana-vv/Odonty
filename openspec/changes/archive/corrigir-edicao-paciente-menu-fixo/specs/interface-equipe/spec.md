## ADDED Requirements

### Requirement: Menu da equipe fixo durante a rolagem em telas largas
Em telas largas, o menu de navegação da equipe SHALL permanecer visível no viewport enquanto a pessoa percorre o conteúdo vertical da tela. Em telas estreitas, o menu SHALL permanecer no fluxo responsivo antes do conteúdo, sem cobrir controles nem introduzir rolagem horizontal.

#### Scenario: Navegar em conteúdo longo no computador
- **WHEN** a pessoa percorre uma tela longa da equipe em viewport larga
- **THEN** o menu continua visível e independente da rolagem do conteúdo

#### Scenario: Acessar a equipe em celular
- **WHEN** a pessoa abre uma tela da equipe em viewport estreita
- **THEN** o menu é apresentado no fluxo responsivo e pode rolar junto da página sem sobrepor o conteúdo
