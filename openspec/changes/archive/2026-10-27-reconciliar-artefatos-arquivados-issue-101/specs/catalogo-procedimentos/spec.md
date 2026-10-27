# catalogo procedimentos Specification

## Purpose

Restaurar na especificação vigente os requisitos aprovados nos deltas arquivados para a capacidade `catalogo-procedimentos`.

## ADDED Requirements

### Requirement: Consulta read-only do catálogo
A interface MUST consultar o catálogo usando o contrato `GET /agenda/opcoes` já disponível no cliente e exibir somente nomes de Procedimentos retornados. A área de navegação MUST ser exclusiva para Administrador, conforme a permissão atual do menu. MUST NOT inventar ou exibir preço, duração, situação, categoria ou outros campos.

#### Scenario: Administrador consulta o catálogo
- **WHEN** uma Conta de Acesso com perfil Administrador abre Procedimentos
- **THEN** a interface carrega as opções autorizadas pelo Xano e exibe seus nomes

#### Scenario: Catálogo vazio ou busca sem correspondência
- **WHEN** o Xano não retorna Procedimentos ou a busca não encontra nome correspondente
- **THEN** a interface mostra uma mensagem apropriada sem ocultar a busca

#### Scenario: Falha de carregamento
- **WHEN** a chamada ao Xano falha
- **THEN** a interface informa que não foi possível carregar o catálogo e oferece nova tentativa sem apresentar dados antigos

#### Scenario: Perfil sem autorização
- **WHEN** uma Recepcionista ou um Profissional tenta acessar a tela diretamente
- **THEN** a interface informa falta de acesso e não solicita opções administrativas

#### Scenario: Xano rejeita a sessão
- **WHEN** o Xano responde com HTTP 401 ou 403 ao carregar o catálogo
- **THEN** a interface limpa a sessão local e apresenta a mensagem segura retornada pela API

