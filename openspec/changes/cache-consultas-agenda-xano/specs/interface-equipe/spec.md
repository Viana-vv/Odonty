## MODIFIED Requirements

### Requirement: Respeito ao limite de requisições do Xano
Durante reruns de interface, o sistema SHALL limitar chamadas repetidas de identificação, reutilizar por sessão a lista de Especialidades por até cinco minutos e reutilizar a lista autorizada de Consultas da mesma data na Agenda por até vinte segundos. Os filtros de busca e situação da Agenda SHALL operar sobre a resposta já carregada durante essa janela. O Xano continua responsável por autorizar cada operação protegida.

#### Scenario: Navegar ou editar sem repetir consultas ao Xano
- **WHEN** a equipe navega entre telas ou edita campos dentro da janela de cache
- **THEN** o app reutiliza a Conta de Acesso por até 20 segundos e as Especialidades por até cinco minutos, sem enviar requisições redundantes

#### Scenario: Filtrar a Agenda durante a janela de cache
- **WHEN** a equipe altera a busca ou a situação da Agenda na mesma Conta de Acesso e data, antes de vinte segundos
- **THEN** o app filtra localmente a resposta autorizada já carregada e não repete `GET /consultas`

#### Scenario: Atualizar uma Consulta ou encerrar a sessão
- **WHEN** uma alteração de Consulta é concluída ou a Conta de Acesso encerra a sessão
- **THEN** o cache da Agenda é descartado e uma leitura posterior usa a Conta de Acesso atual

#### Scenario: Tentar novamente após limite de requisições
- **WHEN** o Xano responde com limite excedido ao carregar Especialidades ou Consultas da Agenda
- **THEN** o app informa a espera e não repete a leitura correspondente antes de vinte segundos
