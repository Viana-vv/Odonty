# registro-evolucao-clinica Specification

## Purpose
Restaurar na especificação vigente os requisitos aprovados nos deltas arquivados para a capacidade `registro-evolucao-clinica`.

## Requirements

### Requirement: Profissional registra evolução clínica no prontuário
A aplicação MUST permitir que um Profissional autenticado registre conteúdo clínico para um Paciente dentro do seu escopo de atendimento. O Registro Clínico deve ser associado ao Prontuário ativo do Paciente, identificar o Profissional autenticado e permanecer no histórico após a criação.

#### Scenario: Registro vinculado a Consulta do Profissional
- **WHEN** um Profissional autorizado seleciona um Paciente e uma Consulta pertencente ao mesmo Paciente e Profissional, informa o conteúdo e salva
- **THEN** o Xano cria um Registro Clínico concluído vinculado ao Prontuário e à Consulta e retorna confirmação sem expor o conteúdo clínico em logs

#### Scenario: Registro sem Consulta
- **WHEN** um Profissional autorizado seleciona um Paciente no seu escopo, informa o conteúdo e salva sem Consulta associada
- **THEN** o Xano cria um Registro Clínico no Prontuário sem associação a uma Consulta

#### Scenario: Conteúdo obrigatório
- **WHEN** o conteúdo clínico está vazio ou contém apenas espaços
- **THEN** a aplicação impede o envio e solicita conteúdo válido

#### Scenario: Profissional não autorizado
- **WHEN** uma Conta de Acesso sem perfil profissional autorizado tenta registrar uma evolução
- **THEN** o Xano rejeita a operação com acesso negado e nenhum Registro Clínico é criado

#### Scenario: Paciente ou Consulta fora do escopo
- **WHEN** o Paciente estiver inativo ou a Consulta não pertencer ao Paciente e ao Profissional autenticado
- **THEN** o Xano rejeita a operação sem alterar o Prontuário

#### Scenario: Contrato não suporta data ou procedimento informados
- **WHEN** o Profissional abre o formulário de nova evolução
- **THEN** a aplicação não sugere que uma data de atendimento ou Procedimento seja gravado pelo contrato atual; a data do Registro Clínico é definida pelo Xano e procedimentos permanecem no fluxo próprio de Consulta
