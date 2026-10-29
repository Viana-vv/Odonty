# fluxo-telas-equipe Specification

## Purpose
TBD - created by archiving change integrar-telas-orfas. Update Purpose after archive.

## Requirements

### Requirement: Acesso da equipe a Exames e Reagendamento
O sistema SHALL oferecer rotas para as telas existentes de Exames e Reagendamento dentro do fluxo autenticado da equipe, apresentando cada rota somente aos perfis já autorizados por seus contratos e mantendo a autorização efetiva no Xano.

#### Cenário: Profissional abre Exames
- **WHEN** uma Conta de Acesso autenticada com perfil Profissional seleciona Exames
- **THEN** o sistema abre a interface existente de Exames com o cliente e a Conta de Acesso atuais

#### Cenário: Administrador ou Recepcionista abre Reagendamento
- **WHEN** uma Conta de Acesso autenticada com perfil Administrador ou Recepcionista seleciona Reagendamento
- **THEN** o sistema abre a interface existente de Reagendamento no mesmo contexto autenticado

#### Cenário: Perfil não autorizado tenta abrir rota diretamente
- **WHEN** uma Conta de Acesso sem perfil autorizado define diretamente uma rota de Exames ou Reagendamento
- **THEN** o sistema não carrega a tela nem consulta dados e retorna a uma área permitida

### Requirement: Procedimentos vinculados à Consulta selecionada
O sistema SHALL abrir a tela existente de Procedimentos da Consulta somente para Profissional autenticado e com uma Consulta selecionada no fluxo da equipe, mantendo o catálogo de Procedimentos como área distinta.

#### Cenário: Profissional abre Procedimentos de uma Consulta
- **WHEN** um Profissional autenticado aciona Procedimentos em uma Consulta de seu fluxo de atendimento
- **THEN** o sistema passa essa Consulta à interface existente e apresenta os Procedimentos vinculados a ela

#### Cenário: Contexto da Consulta ausente ou inválido
- **WHEN** a rota de Procedimentos da Consulta é acessada sem uma Consulta válida selecionada
- **THEN** o sistema não consulta nem altera Procedimentos e orienta o Profissional a selecionar uma Consulta

#### Cenário: Perfil não profissional tenta abrir Procedimentos da Consulta
- **WHEN** uma Conta de Acesso sem perfil Profissional acessa diretamente a rota
- **THEN** o sistema não carrega dados clínicos e retorna a uma área permitida

#### Cenário: Catálogo administrativo permanece distinto
- **WHEN** Administrador abre a área de catálogo Procedimentos
- **THEN** o sistema mantém a tela e o comportamento existentes do catálogo, sem tratá-la como Procedimentos vinculados a uma Consulta

### Requirement: Fallback seguro de integração
O sistema SHALL tratar telas não disponíveis e referências de navegação inválidas sem simular sucesso nem deixar a equipe em uma rota inacessível.

#### Cenário: Módulo integrado não pode ser carregado
- **WHEN** uma Conta de Acesso autorizada seleciona uma área cujo módulo não pode ser importado ou não expõe a função de renderização esperada
- **THEN** o sistema mantém os dados protegidos, apresenta indisponibilidade compreensível e retorna ou permanece em área válida

#### Cenário: Navegar entre áreas sem reaproveitar Consulta antiga
- **WHEN** a equipe sai do contexto de uma Consulta ou seleciona outra Consulta
- **THEN** a navegação descarta ou substitui o contexto anterior para impedir que Procedimentos sejam associados à Consulta errada
