## MODIFIED Requirements

### Requirement: Profissional registra evolução clínica no prontuário

O sistema MUST permitir que Profissional autenticado registre conteúdo clínico no Prontuário ativo do Paciente sob seu escopo, identificando autoria e preservando o histórico. O Xano MUST gravar a Consulta explicitamente validada ou a Consulta encontrada no escopo quando o formulário não informar uma Consulta.

#### Scenario: Registro sem Consulta

- **WHEN** Profissional autorizado salva evolução sem Consulta explícita para Paciente com Prontuário ativo e Consulta no escopo
- **THEN** o Xano encontra a Consulta autorizada e grava seu identificador no Registro Clínico

#### Scenario: Registro vinculado a Consulta do Profissional

- **WHEN** Profissional autorizado salva conteúdo com Consulta pertencente ao mesmo Paciente e Profissional
- **THEN** o Xano valida os vínculos e cria Registro Clínico concluído no Prontuário e na Consulta sem expor conteúdo em logs

#### Scenario: Paciente ou Consulta fora do escopo

- **WHEN** Paciente, Prontuário ou Consulta não estiver no escopo permitido ou o Paciente estiver inativo
- **THEN** o Xano rejeita a operação sem criar Registro Clínico

#### Scenario: Conteúdo obrigatório
- **WHEN** o conteúdo está vazio ou contém apenas espaços
- **THEN** a aplicação impede o envio e solicita conteúdo válido

#### Scenario: Profissional não autorizado
- **WHEN** Conta sem perfil profissional autorizado tenta registrar evolução
- **THEN** o Xano rejeita sem criar Registro Clínico

#### Scenario: Contrato não suporta data ou procedimento informados
- **WHEN** Profissional abre o formulário de evolução
- **THEN** a interface não sugere gravar data de atendimento ou Procedimento pelo contrato atual; o Xano define a data do Registro e Procedimentos permanecem no fluxo de Consulta

