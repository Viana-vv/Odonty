## ADDED Requirements

### Requirement: Consultar histórico individual do Prontuário

O sistema MUST apresentar Registros Clínicos retornados pelo Xano para Paciente sob o escopo da Conta de Acesso autenticada. O seletor de Paciente MUST usar identificadores e nomes retornados pelas rotas existentes. A interface MUST NOT criar dados clínicos, nomes ou autoria que não estejam nas respostas.

#### Scenario: Profissional consulta histórico permitido

- **WHEN** Profissional autenticado abre o histórico individual do Prontuário
- **THEN** o sistema consulta `GET /consultas` e `GET /registros-clinicos` e apresenta somente os Registros Clínicos retornados pelo Xano para o Paciente selecionado

#### Scenario: Paciente consulta conteúdo liberado

- **WHEN** Paciente autenticado abre o histórico individual
- **THEN** o sistema apresenta somente os Registros Clínicos que o Xano retornou como liberados no escopo próprio do Paciente

#### Scenario: Perfil administrativo tenta abrir o histórico clínico

- **WHEN** Administrador ou Recepcionista abre a tela
- **THEN** o sistema não apresenta nem solicita conteúdo clínico

#### Scenario: Histórico vazio ou indisponível

- **WHEN** as rotas retornam coleções vazias ou uma falha segura
- **THEN** o sistema apresenta estado vazio ou erro compreensível sem fabricar conteúdo clínico nem expor detalhes técnicos

### Requirement: Proteger apresentação clínica

A interface MUST evitar registrar conteúdo clínico em logs e MUST tratar o Xano como autoridade de escopo e autorização. O filtro visual por Paciente MUST NOT ampliar o escopo concedido pelo backend.

#### Scenario: Filtrar registros apresentados

- **WHEN** a Conta de Acesso seleciona um Paciente disponível
- **THEN** a interface apresenta apenas os Registros Clínicos retornados que correspondem ao identificador selecionado
