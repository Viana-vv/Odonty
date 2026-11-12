## MODIFIED Requirements

### Requirement: Consultar histórico individual do Prontuário
O sistema MUST apresentar um Prontuário agregado retornado pelo Xano para Paciente sob o escopo da Conta de Acesso autenticada. A interface MUST apresentar dados cadastrais autorizados, seções clínicas, Procedimentos, Exames e Evoluções retornados pelo backend, mantendo estado vazio por seção. A interface MUST NOT criar dados clínicos, nomes, autoria, dentes ou documentos que não estejam nas respostas.

#### Scenario: Profissional consulta histórico permitido
- **WHEN** Profissional autenticado abre o Prontuário individual
- **THEN** o sistema consulta a rota agregada autorizada e apresenta somente os dados retornados pelo Xano para o Paciente selecionado

#### Scenario: Paciente consulta conteúdo liberado
- **WHEN** Paciente autenticado abre o próprio Prontuário
- **THEN** o sistema apresenta dados próprios e somente Registros, Exames, Prescrições, Documentos e seções clínicas liberados

#### Scenario: Perfil administrativo tenta abrir o histórico clínico
- **WHEN** Administrador ou Recepcionista abre a tela
- **THEN** o sistema não apresenta nem solicita conteúdo clínico

#### Scenario: Histórico vazio ou indisponível
- **WHEN** a rota retorna seções vazias ou falha segura
- **THEN** o sistema apresenta o estado vazio ou erro compreensível da seção sem fabricar conteúdo clínico nem expor detalhes técnicos

### Requirement: Proteger apresentação clínica
A interface MUST evitar registrar conteúdo clínico em logs e MUST tratar o Xano como autoridade de escopo e autorização. O filtro visual por Paciente MUST NOT ampliar o escopo concedido pelo backend. A tela MUST limpar conteúdo ao perder a sessão.

#### Scenario: Filtrar registros apresentados
- **WHEN** a Conta de Acesso seleciona um Paciente disponível
- **THEN** a interface apresenta somente as seções retornadas para o identificador selecionado

#### Scenario: Sessão expirada durante a consulta
- **WHEN** uma rota do Prontuário retorna HTTP 401
- **THEN** a interface limpa a sessão local e remove o conteúdo clínico da tela antes de solicitar novo acesso
