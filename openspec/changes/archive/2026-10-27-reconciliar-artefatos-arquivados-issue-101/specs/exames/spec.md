# exames Specification

## Purpose

Restaurar na especificação vigente os requisitos aprovados nos deltas arquivados para a capacidade `exames`.

## ADDED Requirements

### Requirement: Solicitar Exame
O sistema SHALL permitir que um Profissional autenticado solicite um Exame para um Paciente relacionado a uma Consulta autorizada, registrando tipo, data e observações sem anexos.

#### Scenario: Solicitação válida
- **WHEN** um Profissional autorizado envia Paciente, Consulta, tipo e data válidos
- **THEN** o Xano cria o Exame com situação `Solicitado`, registra o evento inicial no histórico e retorna seus dados sem URL de arquivo

#### Scenario: Consulta sem vínculo
- **WHEN** a Consulta informada não pertence ao Paciente ou ao Profissional autenticado
- **THEN** o Xano rejeita a solicitação com erro de autorização e não cria registro

#### Scenario: Data de solicitação futura
- **WHEN** o Profissional envia uma data de solicitação posterior ao momento atual
- **THEN** o Xano rejeita a solicitação e não cria Exame nem histórico

### Requirement: Privacidade e ausência de anexos
O sistema SHALL armazenar apenas solicitação, resultado e observações nesta entrega, sem upload, link público ou referência de arquivo.

#### Scenario: Formulário sem anexo
- **WHEN** o usuário abre a tela de Exames
- **THEN** a interface não oferece upload e informa os campos textuais disponíveis

#### Scenario: Erro de API
- **WHEN** a API falha ao carregar ou salvar um Exame
- **THEN** a interface informa uma mensagem compreensível sem exibir token, stack trace ou conteúdo clínico em logs

### Requirement: Atualizar situação e resultado
O sistema SHALL permitir que o Profissional autorizado avance a situação do Exame em sequência validada, preserve cada transição em histórico imutável e mantenha o resultado informado.

#### Scenario: Resultado liberado
- **WHEN** o Profissional autorizado registra a realização e depois informa resultado válido com situação `Resultado disponível`
- **THEN** o Xano atualiza o Exame e o Paciente passa a visualizar o resultado

#### Scenario: Transições sequenciais com histórico
- **WHEN** o Profissional avança um Exame de `Solicitado` para `Realizado` e depois para `Resultado disponível`
- **THEN** o Xano preserva os dois eventos em registros append-only e mantém a data e o resultado informados

#### Scenario: Transição inválida
- **WHEN** uma Conta tenta alterar situação sem autorização ou avançar para um estado não permitido
- **THEN** o Xano rejeita a alteração com conflito ou acesso negado e preserva os dados e o histórico anteriores

#### Scenario: Data ou resultado inválido
- **WHEN** a realização antecede a solicitação, está no futuro ou o Profissional tenta liberar resultado vazio
- **THEN** o Xano rejeita a alteração e preserva o Exame e seu histórico

### Requirement: Consultar Exames autorizados
O sistema SHALL listar Exames conforme o perfil autenticado e SHALL exibir resultado clínico ao Paciente somente quando a situação for `Resultado disponível`.

#### Scenario: Paciente consulta os próprios Exames
- **WHEN** um Paciente autenticado solicita sua lista
- **THEN** o Xano retorna somente Exames do próprio Paciente e oculta resultado enquanto não estiver disponível

#### Scenario: Profissional consulta Exames relacionados
- **WHEN** um Profissional autenticado solicita sua lista
- **THEN** o Xano retorna somente Exames de Pacientes e Consultas sob sua autorização

#### Scenario: Perfil sem autorização
- **WHEN** uma Conta de Acesso sem permissão clínica solicita Exames
- **THEN** o Xano rejeita a operação sem expor dados clínicos

