## ADDED Requirements

### Requirement: Navegação pelas telas do kit
O sistema SHALL apresentar navegação para as áreas representadas no kit de referência, respeitando o perfil da Conta de Acesso e distinguindo operações reais do Xano das operações em modo demonstrativo.

#### Scenario: Conta autenticada acessa uma área permitida
- **WHEN** Administrador, Recepcionista ou Profissional seleciona uma área permitida ao seu perfil
- **THEN** o sistema apresenta a tela correspondente com título, conteúdo, ações e hierarquia visual consistentes com o kit

#### Scenario: Perfil sem permissão tenta acessar uma área restrita
- **WHEN** uma Conta de Acesso tenta abrir uma área não autorizada ao seu perfil
- **THEN** a interface não apresenta os dados nem permite executar a operação, e a autorização permanece validada pelo Xano

#### Scenario: Usar área sem integração Xano no modo demonstrativo
- **WHEN** a equipe abre uma área sem contrato de API confirmado enquanto o modo demonstrativo está ativo
- **THEN** a interface apresenta a operação de demonstração com aviso visível de que os dados são fictícios e mantidos somente na sessão

#### Scenario: Manter áreas sem integração fora do modo demonstrativo
- **WHEN** a equipe abre uma área sem contrato Xano confirmado e o modo demonstrativo está desativado
- **THEN** a interface informa que a operação ainda não está disponível, sem simular sucesso nem alterar dados reais

### Requirement: Remoção do cabeçalho e rodapé visuais atuais
O sistema SHALL deixar de exibir o rodapé atual e o cabeçalho visual da aplicação nas telas de login e da equipe, mantendo controles essenciais do Streamlit que sejam necessários para navegação, acessibilidade e funcionamento.

#### Scenario: Abrir o login ou uma tela autenticada
- **WHEN** uma pessoa abre o login ou navega pela área autenticada
- **THEN** não vê o cabeçalho nem o rodapé visuais atuais e consegue utilizar todos os controles funcionais da tela

### Requirement: Identidade visual responsiva do kit
As telas abrangidas SHALL seguir a paleta, hierarquia, tipografia, cartões, formulários e padrões de navegação do kit e permanecer utilizáveis em computador, tablet, celular e teclado.

#### Scenario: Usar a aplicação em tela estreita
- **WHEN** uma pessoa abre as telas em uma viewport de celular
- **THEN** conteúdo e navegação se reorganizam sem sobreposição ou rolagem horizontal da página

#### Scenario: Navegar usando teclado
- **WHEN** uma pessoa percorre navegação, formulários e ações somente com teclado
- **THEN** os controles recebem foco em ordem compreensível e o foco permanece visível

### Requirement: Dados fictícios coerentes no modo demonstrativo
O sistema SHALL usar somente dados fictícios no modo demonstrativo, manter seus relacionamentos coerentes entre telas e identificá-los como dados de demonstração, sem misturá-los com respostas do Xano ou alegar persistência após a sessão.

#### Scenario: Dados relacionados aparecem entre telas demonstrativas
- **WHEN** um Paciente fictício é cadastrado no modo demonstrativo
- **THEN** ele pode ser selecionado nas telas demonstrativas de Consulta e Prontuário usando o mesmo identificador e seus relacionamentos de domínio

#### Scenario: Informar limites da persistência demonstrativa
- **WHEN** uma pessoa acessa uma tela no modo demonstrativo
- **THEN** a interface informa que alterações vivem somente na sessão e podem ser perdidas ao reiniciar ou encerrar o app

### Requirement: Estado vazio sem conteúdo clínico inventado
O sistema SHALL apresentar estados vazios compreensíveis quando uma listagem ou histórico não possuir dados, sem preencher o estado vazio com registros clínicos fabricados dinamicamente.

#### Scenario: Abrir listagem sem registros
- **WHEN** a fonte de dados confirmada retorna uma coleção vazia
- **THEN** a tela explica que não há registros e apresenta somente ações permitidas e implementadas

#### Scenario: Abrir prontuário sem registros clínicos
- **WHEN** o prontuário do Paciente não possui registros clínicos disponíveis
- **THEN** o histórico permanece vazio e orienta sobre a ação autorizada para registrar uma evolução

### Requirement: Cobertura unitária dos contratos REST
Cada contrato REST `GET` ou `POST` utilizado pela aplicação SHALL possuir pelo menos um teste unitário em Python e um teste unitário em JavaScript que verifiquem método, rota, formato de entrada ou resposta e comportamento de erro sem enviar requisições reais à rede.

#### Scenario: Adicionar ou alterar contrato GET
- **WHEN** um contrato `GET` é introduzido ou alterado
- **THEN** a suíte Python cobre o comportamento do cliente e a suíte JavaScript verifica a correspondência entre rota, método e export Xano

#### Scenario: Adicionar ou alterar contrato POST
- **WHEN** um contrato `POST` é introduzido ou alterado
- **THEN** a suíte Python cobre payload, resposta e falhas, e a suíte JavaScript verifica a correspondência entre rota, método e export Xano

### Requirement: Respeito ao limite de requisições do Xano
Durante reruns de interface, o sistema SHALL limitar chamadas repetidas de identificação e reutilizar, por sessão, a lista de Especialidades por até cinco minutos. O Xano continua responsável por autorizar cada operação protegida.

#### Scenario: Navegar ou editar sem repetir consultas ao Xano
- **WHEN** a equipe navega entre telas ou edita campos dentro da janela de cache
- **THEN** o app reutiliza a Conta de Acesso por até 20 segundos e as Especialidades por até cinco minutos, sem enviar requisições redundantes

#### Scenario: Tentar novamente após limite de requisições
- **WHEN** o Xano responde com limite excedido ao carregar Especialidades
- **THEN** o app informa a espera e não repete a requisição antes de 20 segundos
