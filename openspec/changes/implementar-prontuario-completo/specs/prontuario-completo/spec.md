## Purpose

Fornecer um Prontuário clínico e odontológico completo, organizado por seções, com dados autorizados pelo Xano e histórico preservado para Profissionais e Pacientes.

## ADDED Requirements

### Requirement: Consultar Prontuário agregado autorizado
O sistema SHALL oferecer uma consulta agregada do Prontuário por Paciente, incluindo dados cadastrais autorizados e as seções Anamnese, Histórico Odontológico, Odontograma, Exame Clínico, Diagnósticos, Plano de Tratamento, Procedimentos, Exames, Prescrições, Evoluções e Documentos. Coleções sem dados SHALL ser retornadas vazias, sem conteúdo inventado.

#### Scenario: Profissional consulta Prontuário do escopo
- **WHEN** um Profissional ativo consulta um Paciente relacionado ao seu atendimento
- **THEN** o Xano retorna o resumo e somente as seções clínicas autorizadas, sem dados de outro Paciente

#### Scenario: Paciente consulta o próprio Prontuário
- **WHEN** um Paciente autenticado consulta o próprio identificador
- **THEN** o sistema retorna seus dados permitidos e somente conteúdos clínicos liberados pela clínica

#### Scenario: Perfil administrativo tenta consultar conteúdo clínico
- **WHEN** Administrador ou Recepcionista chama a rota de Prontuário
- **THEN** o Xano nega ou retorna somente dados administrativos explicitamente permitidos, sem conteúdo clínico

#### Scenario: Paciente com Prontuário sem Consulta ou Registro
- **WHEN** o Paciente possui Prontuário ativo, mas ainda não possui Consulta ou Registro Clínico
- **THEN** ele continua aparecendo no escopo autorizado e a resposta retorna as seções vazias

### Requirement: Exibir dados cadastrais do Paciente
O sistema SHALL apresentar no Prontuário nome, CPF, data de nascimento, telefone e endereço quando esses dados existirem e forem autorizados. Campo ausente SHALL ser exibido como não informado, sem valor fictício.

#### Scenario: Dados cadastrais disponíveis
- **WHEN** o Xano retorna os dados cadastrais autorizados
- **THEN** a tela apresenta os campos no resumo do Paciente

#### Scenario: Endereço ausente
- **WHEN** o Paciente não possui endereço cadastrado
- **THEN** a tela informa que o endereço não foi informado e mantém o restante do Prontuário disponível

### Requirement: Registrar seções clínicas com histórico
O sistema SHALL permitir que Profissional ativo autorizado registre Anamnese, Histórico Odontológico, Exame Clínico, Diagnóstico, Plano de Tratamento, Odontograma, Prescrição e Documento conforme a seção, mantendo autor, Consulta quando aplicável, data, liberação e versão. Alterações SHALL preservar versões anteriores.

#### Scenario: Profissional registra seção
- **WHEN** Profissional autorizado envia conteúdo válido para o Paciente no seu escopo
- **THEN** o Xano cria uma versão vinculada ao Prontuário e mantém a versão anterior intacta

#### Scenario: Seção fora do escopo
- **WHEN** uma Conta envia identificador de Paciente ou Consulta não autorizado
- **THEN** o Xano rejeita sem gravar conteúdo clínico ou confirmar dados de terceiros

#### Scenario: Conteúdo inválido
- **WHEN** a seção obrigatória está vazia, possui tipo inválido ou excede o limite definido
- **THEN** a API retorna erro seguro e a interface informa o campo corrigível

### Requirement: Integrar Procedimentos, Exames e Evoluções
O sistema SHALL apresentar no agregado os Procedimentos relacionados, Exames existentes e Evoluções Clínicas, sem duplicar registros nem converter uma entidade em outra.

#### Scenario: Procedimentos e Exames relacionados
- **WHEN** o Paciente possui Procedimentos ou Exames autorizados
- **THEN** a tela os apresenta nas seções próprias com Consulta, data, situação e Profissional quando disponíveis

#### Scenario: Evolução legada
- **WHEN** existe Registro Clínico textual criado antes da estruturação
- **THEN** ele aparece na seção Evolução Clínica com conteúdo original, data, autoria e retificações

### Requirement: Proteger arquivos e documentos clínicos
O sistema SHALL armazenar apenas referências privadas de imagens e Documentos, validar tipo e tamanho e exigir autorização para listagem e download. A API SHALL NOT retornar URL pública permanente.

#### Scenario: Documento autorizado
- **WHEN** Profissional autorizado ou Paciente com liberação lista Documentos
- **THEN** o sistema retorna metadados permitidos e oferece acesso protegido conforme o escopo

#### Scenario: Documento sem autorização
- **WHEN** Conta sem escopo solicita metadados ou download
- **THEN** o Xano rejeita sem retornar referência privada ou confirmar o arquivo

### Requirement: Preservar histórico e privacidade
O sistema SHALL impedir exclusão física de seções clínicas, manter versões e retificações e não registrar conteúdo clínico, tokens ou arquivos em logs. Logout ou perda de acesso SHALL remover conteúdo clínico da sessão local.

#### Scenario: Retificação
- **WHEN** Profissional autorizado corrige uma seção concluída com justificativa
- **THEN** o sistema registra nova versão vinculada e mantém o conteúdo anterior auditável

#### Scenario: Sessão expirada
- **WHEN** uma consulta do Prontuário retorna sessão expirada
- **THEN** a interface limpa a sessão, remove o conteúdo clínico exibido e solicita novo acesso
