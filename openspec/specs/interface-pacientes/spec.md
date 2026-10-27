# interface-pacientes Specification

## Purpose
Restaurar na especificação vigente os requisitos aprovados nos deltas arquivados para a capacidade `interface-pacientes`.

## Requirements

### Requirement: Privacidade da listagem
A interface SHALL usar exclusivamente a rota GET `/agenda/opcoes` existente, que retorna `id` e `nome` dos Pacientes e autoriza Administrador e Recepcionista. A interface SHALL NOT solicitar, exibir ou inferir outros dados do Paciente, nem criar ou alterar cadastros.

#### Scenario: Dados mínimos da API
- **WHEN** a lista é carregada com sucesso
- **THEN** somente o identificador e o nome recebidos da API são exibidos

#### Scenario: Recursos de cadastro indisponíveis nesta tela
- **WHEN** o usuário consulta a listagem
- **THEN** não são oferecidas ações para cadastrar, editar, inativar ou consultar detalhes do Paciente

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

### Requirement: Reutilização da resposta por sessão
A interface SHALL reutilizar a resposta bem-sucedida de Pacientes durante a sessão por até 20 segundos para que a busca local e os reruns do Streamlit não repitam a chamada ao Xano. A interface SHALL oferecer atualização manual, SHALL NOT armazenar respostas de erro e SHALL limpar os dados ao encerrar ou invalidar a sessão.

#### Scenario: Busca local após carregamento
- **WHEN** o usuário altera o texto de busca após carregar a lista
- **THEN** a interface filtra os dados da sessão sem enviar outro GET ao Xano

#### Scenario: Atualização solicitada
- **WHEN** o usuário aciona Atualizar
- **THEN** a interface faz uma nova solicitação GET e exibe a resposta atual

#### Scenario: Resposta de erro
- **WHEN** a solicitação GET falha
- **THEN** a falha não é cacheada e uma nova tentativa pode carregar dados atuais
