## ADDED Requirements

### Requirement: Consulta read-only do catálogo
A interface MUST consultar o catálogo usando o contrato `GET /agenda/opcoes` já disponível no cliente e exibir somente nomes de Procedimentos retornados. MUST NOT inventar ou exibir preço, duração, situação, categoria ou outros campos.

#### Scenario: Administrador ou Recepcionista consulta o catálogo
- **WHEN** uma Conta de Acesso com perfil Administrador ou Recepcionista abre Procedimentos
- **THEN** a interface carrega as opções autorizadas pelo Xano e exibe seus nomes

#### Scenario: Catálogo vazio ou busca sem correspondência
- **WHEN** o Xano não retorna Procedimentos ou a busca não encontra nome correspondente
- **THEN** a interface mostra uma mensagem apropriada sem ocultar a busca

#### Scenario: Falha de carregamento
- **WHEN** a chamada ao Xano falha
- **THEN** a interface informa que não foi possível carregar o catálogo e oferece nova tentativa sem apresentar dados antigos

#### Scenario: Perfil sem autorização
- **WHEN** um Profissional abre a tela
- **THEN** a interface informa falta de acesso e não solicita opções administrativas
