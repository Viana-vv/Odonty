## MODIFIED Requirements

### Requirement: Privacidade e ausência de anexos
O sistema SHALL armazenar apenas solicitação, resultado e observações nesta entrega, sem upload, link público ou referência de arquivo. Quando uma operação de Exame falhar por dados corrigíveis, permissão, escopo, conflito ou limite de requisições, a interface SHALL apresentar orientação compreensível e segura, sem expor token, stack trace ou conteúdo clínico em logs.

#### Scenario: Formulário sem anexo
- **WHEN** o usuário abre a tela de Exames
- **THEN** a interface não oferece upload e informa os campos textuais disponíveis

#### Scenario: Campo obrigatório ausente na solicitação
- **WHEN** o Profissional tenta solicitar um Exame sem Paciente, Consulta ou tipo
- **THEN** a interface informa qual campo deve ser preenchido e não envia uma solicitação inválida

#### Scenario: Data ou observação inválida
- **WHEN** o Profissional informa data inválida, data futura ou observações acima do limite permitido
- **THEN** a interface informa a correção necessária e não envia uma solicitação inválida

#### Scenario: Erro de API
- **WHEN** a API falha ao carregar, solicitar ou atualizar um Exame
- **THEN** a interface apresenta uma mensagem segura específica para a situação conhecida ou uma orientação genérica para falha inesperada, sem expor detalhes técnicos ou clínicos

### Requirement: Solicitar Exame
O sistema SHALL permitir que um Profissional autenticado solicite um Exame para um Paciente relacionado a uma Consulta autorizada, registrando tipo, data e observações sem anexos. A interface SHALL deixar claro que a solicitação é registrada para o Paciente e a Consulta selecionados e permanece inicialmente em `Solicitado`.

#### Scenario: Solicitação válida
- **WHEN** um Profissional autorizado envia Paciente, Consulta, tipo e data válidos
- **THEN** o Xano cria o Exame com situação `Solicitado`, registra o evento inicial no histórico e retorna seus dados sem URL de arquivo

#### Scenario: Destino da solicitação
- **WHEN** o Profissional confirma a solicitação no formulário
- **THEN** a operação é vinculada ao Paciente e à Consulta selecionados, sem encaminhamento automático para laboratório, profissional externo ou notificação fora do sistema

#### Scenario: Consulta sem vínculo
- **WHEN** a Consulta informada não pertence ao Paciente ou ao Profissional autenticado
- **THEN** o Xano rejeita a solicitação com erro de autorização e a interface informa que o vínculo não está no escopo permitido

#### Scenario: Data de solicitação futura
- **WHEN** o Profissional envia uma data de solicitação posterior ao momento atual
- **THEN** o Xano rejeita a solicitação e não cria Exame nem histórico, e a interface orienta o preenchimento de uma data válida
