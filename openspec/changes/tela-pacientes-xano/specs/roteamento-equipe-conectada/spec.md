## Purpose

Permite que as áreas conectadas sejam abertas por módulos independentes conforme perfil, mantendo opções ainda não integradas indisponíveis e sem falhas no roteamento comum.

## ADDED Requirements

### Requirement: Roteamento de módulos conectados
O sistema SHALL abrir uma área conectada por seu módulo isolado somente quando o módulo estiver disponível e a Conta de Acesso tiver perfil permitido. Áreas sem módulo integrado SHALL permanecer indisponíveis, inclusive quando acessadas por estado de sessão adulterado. O modo de demonstração SHALL manter seu roteamento existente.

#### Scenario: Módulo autorizado disponível
- **WHEN** uma Conta de Acesso autorizada seleciona uma área conectada cujo módulo existe
- **THEN** o roteador chama o módulo correspondente com o cliente e a Conta de Acesso

#### Scenario: Módulo ainda não integrado
- **WHEN** uma área conectada não possui módulo de tela integrado
- **THEN** a área é apresentada como indisponível e nenhuma tela substituta é renderizada

#### Scenario: Perfil sem acesso altera o estado da sessão
- **WHEN** uma Conta de Acesso tenta abrir diretamente uma área para a qual não tem perfil permitido
- **THEN** o roteador retorna à Visão geral sem carregar o módulo

#### Scenario: Modo de demonstração
- **WHEN** o sistema está no modo de demonstração
- **THEN** as áreas continuam sendo renderizadas pelo fluxo de demonstração existente

### Requirement: Atalho para Nova Consulta
O sistema SHALL oferecer à Administração e Recepção um acesso à tela Nova Consulta na Visão geral e na Agenda quando o módulo estiver integrado. Enquanto o módulo estiver ausente, os atalhos SHALL permanecer indisponíveis. O Profissional SHALL NOT receber esses atalhos.

#### Scenario: Administrador ou Recepcionista e módulo disponível
- **WHEN** Administrador ou Recepcionista abre a Visão geral ou a Agenda e o módulo Nova Consulta existe
- **THEN** um atalho navega para a tela Nova Consulta

#### Scenario: Módulo Nova Consulta ausente
- **WHEN** Administrador ou Recepcionista abre a Visão geral ou a Agenda e o módulo não existe
- **THEN** o atalho não permite navegar e informa que a integração ainda não está disponível

#### Scenario: Profissional sem permissão para agendar
- **WHEN** Profissional abre a Visão geral ou a Agenda
- **THEN** os atalhos para Nova Consulta não são apresentados
