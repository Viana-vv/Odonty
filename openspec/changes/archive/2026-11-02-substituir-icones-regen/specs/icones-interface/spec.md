## Purpose

Unificar os ícones das interfaces existentes com vetores locais do Regen Icons, mantendo acessibilidade, identidade visual e operações disponíveis por perfil.

## ADDED Requirements

### Requirement: Iconografia consistente e local
O sistema SHALL apresentar ícones Regen nas áreas de navegação, indicadores, ações e controles das telas existentes, incluindo equipe, Paciente e demonstração, sem solicitar recursos gráficos externos.

#### Scenario: Navegar entre telas
- **WHEN** uma pessoa abre um painel, listagem, formulário ou área de acompanhamento autorizada
- **THEN** os ícones seguem a mesma família e preservam proporções e contraste em desktop e celular.

### Requirement: Recursos gráficos sem conteúdo ativo
O sistema SHALL utilizar somente vetores revisados de uma versão identificada, sem scripts, eventos, referências externas ou dependências executáveis do gerador.

#### Scenario: Recurso inválido
- **WHEN** um vetor contém conteúdo ativo ou referência externa
- **THEN** a verificação rejeita sua inclusão.

### Requirement: Preservação da interface e dos acessos
O sistema SHALL preservar imagens, mascotes, marca, composição, rótulos acessíveis, controles e permissões existentes durante a troca dos ícones.

#### Scenario: Acionar um controle
- **WHEN** uma pessoa aciona um botão pelo mouse ou teclado
- **THEN** a operação e o nome acessível permanecem disponíveis, e o ícone decorativo não duplica o anúncio.

#### Scenario: Acesso restrito
- **WHEN** uma Conta de Acesso não possui permissão para uma operação
- **THEN** a troca dos ícones não disponibiliza essa operação nem modifica a autorização existente.
