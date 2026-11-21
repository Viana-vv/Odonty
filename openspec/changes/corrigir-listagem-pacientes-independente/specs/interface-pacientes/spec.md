## MODIFIED Requirements

### Requirement: Privacidade da listagem
A interface SHALL carregar a listagem exclusivamente por GET `/pacientes`, que retorna somente `id` e `nome` dos Pacientes ativos e autoriza Administrador e Recepcionista no Xano. A listagem SHALL NOT solicitar ou inferir outros dados do Paciente. As ações existentes de cadastro e edição SHALL continuar usando seus contratos autorizados próprios.

#### Scenario: Dados mínimos da API
- **WHEN** a lista é carregada com sucesso
- **THEN** somente o identificador e o nome recebidos da API são exibidos

#### Scenario: Recursos de cadastro indisponíveis nesta tela
- **WHEN** o usuário apenas consulta a listagem
- **THEN** nenhum contrato de criação, edição ou detalhe é chamado

#### Scenario: Opções da Agenda inválidas
- **WHEN** uma Recepcionista abre Pacientes e existe um Profissional sem nome ou uma falha nas opções da Agenda
- **THEN** a tela carrega os Pacientes sem consultar Profissionais, Procedimentos ou GET `/agenda/opcoes`

#### Scenario: Sem autenticação ou permissão
- **WHEN** uma solicitação não possui sessão válida ou pertence somente a Paciente ou Profissional
- **THEN** o Xano recusa a solicitação sem retornar a lista administrativa

#### Scenario: Lista vazia
- **WHEN** não existem Pacientes ativos
- **THEN** GET `/pacientes` retorna `pacientes` como lista vazia e a interface mostra o estado vazio existente

#### Scenario: Falha na rota de Pacientes
- **WHEN** GET `/pacientes` falha ou retorna dados inválidos
- **THEN** a interface apresenta mensagem compreensível sem exibir detalhes privados nem armazenar a falha em cache
