## MODIFIED Requirements

### Requirement: Consulta read-only do catálogo
A interface MUST consultar o catálogo usando GET `/procedimentos` e exibir somente nomes de Procedimentos retornados. A área de navegação e a rota MUST permitir Administrador e Recepcionista com sessão válida e conta ativa. MUST NOT inventar ou exibir preço, duração, situação, categoria ou outros campos. O catálogo MUST NOT depender de Pacientes, Profissionais ou GET `/agenda/opcoes`.

#### Scenario: Administrador consulta o catálogo
- **WHEN** uma Conta de Acesso com perfil Administrador abre Procedimentos
- **THEN** a interface carrega os Procedimentos autorizados pelo Xano e exibe seus nomes

#### Scenario: Recepcionista consulta o catálogo
- **WHEN** uma Recepcionista autenticada usa o menu Procedimentos
- **THEN** a tela abre e consulta GET `/procedimentos`, sem ações para alterar cadastros

#### Scenario: Catálogo vazio ou busca sem correspondência
- **WHEN** o Xano não retorna Procedimentos ou a busca não encontra nome correspondente
- **THEN** a interface mostra uma mensagem apropriada sem ocultar a busca

#### Scenario: Falha de carregamento
- **WHEN** a chamada ao Xano falha
- **THEN** a interface informa que não foi possível carregar o catálogo e oferece nova tentativa sem apresentar dados antigos

#### Scenario: Perfil sem autorização
- **WHEN** um Paciente ou um Profissional tenta acessar a tela ou a rota diretamente
- **THEN** o acesso é recusado sem apresentar o catálogo

#### Scenario: Xano rejeita a sessão
- **WHEN** o Xano responde com HTTP 401 ou 403 ao carregar o catálogo
- **THEN** a interface limpa a sessão local e apresenta mensagem segura

#### Scenario: Profissional incompleto na Agenda
- **WHEN** existe um Profissional incompleto ou as opções da Agenda estão indisponíveis
- **THEN** a consulta do catálogo permanece funcional sem chamar essas opções
