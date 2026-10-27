# autoatendimento paciente Specification

## Purpose

Restaurar na especificação vigente os requisitos aprovados nos deltas arquivados para a capacidade `autoatendimento-paciente`.

## ADDED Requirements

### Requirement: Consultar Registros Clínicos liberados
O sistema MUST consultar Registros Clínicos pelo contrato `GET /registros-clinicos`, sem confiar em identificador de Paciente fornecido pela interface. O Xano MUST derivar o Paciente da sessão e retornar somente Registros Clínicos próprios com `liberado_paciente=true`. A interface MUST apresentar conteúdo, data e profissional responsável disponíveis no contrato, sem permitir alteração.

#### Scenario: Há Registros Clínicos liberados
- **WHEN** o Paciente autenticado consulta seus conteúdos liberados
- **THEN** são apresentados somente os Registros Clínicos do próprio Paciente explicitamente liberados

#### Scenario: Registro não liberado ou pertencente a terceiro
- **WHEN** um Registro Clínico não está liberado ou pertence a outro Paciente
- **THEN** o Xano não o retorna ao Paciente

### Requirement: Consultar Exames com resultado liberado
O sistema MUST consultar Exames pelo contrato `GET /exames`, sem confiar em identificador de Paciente fornecido pela interface. O Xano MUST derivar o Paciente da sessão e somente preencher o resultado quando a situação do Exame for `Resultado disponível`. A interface MUST NOT expor referências de arquivo público nem permitir alterar Exame ou resultado.

#### Scenario: Exame com resultado disponível
- **WHEN** o Paciente autenticado consulta seus Exames e um Exame possui situação `Resultado disponível`
- **THEN** o sistema apresenta os dados retornados e o resultado liberado

#### Scenario: Exame sem resultado disponível
- **WHEN** o Exame próprio ainda não possui resultado liberado
- **THEN** o sistema apresenta situação e dados administrativos permitidos sem revelar o resultado

#### Scenario: Exame de outro Paciente
- **WHEN** a Conta de Acesso tenta consultar Exame pertencente a outro Paciente
- **THEN** o Xano impede a consulta e não revela a existência do Exame

### Requirement: Consultar Consultas próprias
O sistema MUST apresentar as Consultas passadas e futuras do Paciente autenticado usando `GET /consultas` sem enviar `paciente_id`. A interface MUST apresentar somente data, horário, Profissional e situação, MUST NOT apresentar Procedimentos ou dados clínicos e MUST orientar solicitação de cancelamento futura à clínica, sem oferecer agendamento ou cancelamento.

#### Scenario: Consultas próprias carregadas
- **WHEN** o Paciente autenticado abre sua área
- **THEN** o sistema organiza as Consultas por data no fuso `America/Sao_Paulo` e mostra somente os campos administrativos permitidos

#### Scenario: Consultas vazias ou API indisponível
- **WHEN** não há Consultas no período ou a API falha
- **THEN** o sistema mostra estado vazio ou erro compreensível sem dados técnicos

### Requirement: Sessão independente do Paciente
O sistema MUST oferecer um entrypoint de autoatendimento separado do entrypoint da equipe, autenticar a Conta de Acesso pelo Xano e apresentar conteúdo somente quando o backend confirmar o perfil Paciente ativo. A senha MUST NOT permanecer após o processamento, e credenciais MUST NOT ser persistidas para restaurar a sessão após perda do estado do Streamlit.

#### Scenario: Paciente entra com conta ativa
- **WHEN** uma Conta de Acesso ativa com perfil Paciente autentica com sucesso
- **THEN** o sistema apresenta a área própria do Paciente e mantém a credencial apenas no estado temporário da sessão Streamlit

#### Scenario: Conta não autorizada
- **WHEN** a autenticação, identidade ou tentativa de operação protegida falha por sessão inválida ou perfil sem autorização
- **THEN** o sistema bloqueia o conteúdo protegido, limpa a sessão local e apresenta mensagem segura

#### Scenario: Perda de estado ou logout
- **WHEN** o estado da sessão é perdido ou o Paciente solicita saída
- **THEN** o sistema exige nova autenticação e limpa a credencial local; o encerramento remoto só é afirmado quando confirmado pelo Xano

### Requirement: Interface do Paciente conforme kit Sorriso Mais
O sistema MUST manter identidade visual, hierarquia, cores, espaçamentos, legibilidade e adaptação responsiva compatíveis com o kit Sorriso Mais, preservando os controles funcionais e mensagens acessíveis.

#### Scenario: Acesso em computador e dispositivo móvel
- **WHEN** o Paciente consulta sua área em diferentes larguras de tela
- **THEN** os controles e conteúdos continuam legíveis, ordenados e operáveis sem sobreposição

