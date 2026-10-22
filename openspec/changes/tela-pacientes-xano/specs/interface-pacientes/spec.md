## Purpose

Permite que Administrador e Recepcionista localizem Pacientes ativos no modo conectado usando somente as informações administrativas disponibilizadas pela API autorizada.

## ADDED Requirements

### Requirement: Listagem conectada de Pacientes
O sistema SHALL apresentar a lista de Pacientes ativos fornecida pela API, mostrando somente identificador e nome. A lista SHALL permitir busca por nome e SHALL apresentar estados de carregamento, erro e lista vazia sem inserir dados fictícios.

#### Scenario: Lista de Pacientes carregada
- **WHEN** um Administrador ou Recepcionista abre Pacientes e a API retorna itens
- **THEN** a interface apresenta identificador e nome de cada Paciente e permite filtrar pelo nome

#### Scenario: Nenhum Paciente disponível
- **WHEN** a API retorna uma lista vazia ou a busca não encontra correspondências
- **THEN** a interface apresenta uma mensagem de lista vazia sem exibir registros demonstrativos

#### Scenario: Falha ao carregar Pacientes
- **WHEN** a API retorna erro ou a conexão falha
- **THEN** a interface apresenta uma mensagem compreensível sem expor detalhes técnicos nem dados fictícios

#### Scenario: Acesso sem autorização
- **WHEN** uma Conta de Acesso sem permissão tenta carregar a lista
- **THEN** a autorização é recusada pelo Xano e a interface apresenta o erro sem revelar dados

### Requirement: Privacidade da listagem
A interface SHALL usar exclusivamente a rota GET `/agenda/opcoes` existente, que retorna `id` e `nome` dos Pacientes e autoriza Administrador e Recepcionista. A interface SHALL NOT solicitar, exibir ou inferir outros dados do Paciente, nem criar ou alterar cadastros.

#### Scenario: Dados mínimos da API
- **WHEN** a lista é carregada com sucesso
- **THEN** somente o identificador e o nome recebidos da API são exibidos

#### Scenario: Recursos de cadastro indisponíveis nesta tela
- **WHEN** o usuário consulta a listagem
- **THEN** não são oferecidas ações para cadastrar, editar, inativar ou consultar detalhes do Paciente
