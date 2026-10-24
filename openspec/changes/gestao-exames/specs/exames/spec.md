## Purpose

Permitir que profissionais solicitem exames e registrem resultados no Xano, com acesso controlado ao paciente e uma tela coerente com o kit visual Sorriso Mais.

## ADDED Requirements

### Requirement: Solicitar exame
O sistema SHALL permitir que um profissional autenticado solicite um exame para um Paciente relacionado a uma Consulta autorizada, registrando tipo, data e observações sem anexos.

#### Scenario: Solicitação válida
- **WHEN** um profissional autorizado envia paciente, consulta, tipo e data válidos
- **THEN** o Xano cria o exame com situação `Solicitado` e retorna seus dados sem URL de arquivo

#### Scenario: Consulta sem vínculo
- **WHEN** a consulta informada não pertence ao paciente ou ao profissional autenticado
- **THEN** o Xano rejeita a solicitação com erro de autorização e não cria registro

### Requirement: Consultar exames autorizados
O sistema SHALL listar exames conforme o perfil autenticado e SHALL exibir resultado clínico ao Paciente somente quando a situação for `Resultado disponível`.

#### Scenario: Paciente consulta os próprios exames
- **WHEN** um Paciente autenticado solicita sua lista
- **THEN** o Xano retorna somente exames do próprio paciente e oculta resultado enquanto não estiver disponível

#### Scenario: Profissional consulta exames relacionados
- **WHEN** um profissional autenticado solicita sua lista
- **THEN** o Xano retorna somente exames de pacientes e consultas sob sua autorização

#### Scenario: Perfil sem autorização
- **WHEN** uma Conta de Acesso sem permissão clínica solicita exames
- **THEN** o Xano rejeita a operação sem expor dados clínicos

### Requirement: Atualizar situação e resultado
O sistema SHALL permitir que o profissional autorizado avance a situação do exame de forma validada, preservando o histórico e o resultado informado.

#### Scenario: Resultado liberado
- **WHEN** o profissional autorizado informa resultado válido e situação `Resultado disponível`
- **THEN** o Xano atualiza o exame e o Paciente passa a visualizar o resultado

#### Scenario: Transição inválida
- **WHEN** uma Conta tenta alterar situação sem autorização ou usar estado não previsto
- **THEN** o Xano rejeita a alteração e preserva os dados anteriores

### Requirement: Privacidade e ausência de anexos
O sistema SHALL armazenar apenas solicitação, resultado e observações nesta entrega, sem upload, link público ou referência de arquivo.

#### Scenario: Formulário sem anexo
- **WHEN** o usuário abre a tela de exames
- **THEN** a interface não oferece upload e informa os campos textuais disponíveis

#### Scenario: Erro de API
- **WHEN** a API falha ao carregar ou salvar um exame
- **THEN** a interface informa uma mensagem compreensível sem exibir token, stack trace ou conteúdo clínico em logs
