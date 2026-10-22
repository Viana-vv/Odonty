# Proposal

## Why

A equipe não consegue cadastrar pelo site os horários em que os profissionais estarão disponíveis, então a Agenda não oferece horários para novas Consultas. A tela precisa permitir que Administração e Recepção registrem uma Disponibilidade e recebam retorno claro quando o Xano rejeitar o intervalo.

## What Changes

- Adicionar à Agenda uma ação para abrir o formulário de cadastro de Disponibilidade.
- Permitir selecionar Profissional, data, horário inicial e horário final, com validação dos campos e apresentação dos conflitos retornados pelo Xano.
- Enviar a criação pela API REST existente, mantendo autenticação, autorização e validações de negócio no Xano.
- Atualizar a Agenda após sucesso para que a nova Disponibilidade possa ser usada no agendamento.
- Limitar esta entrega a um intervalo por cadastro; recorrência e edição ou bloqueio de horários ficam fora do escopo.

## Capabilities

### New Capabilities

- `gestao-disponibilidades`: cadastro de Disponibilidades pela equipe na Agenda.

### Modified Capabilities

Nenhuma.

## Impact

- Interface Streamlit da Agenda e cliente REST Xano.
- Endpoint existente `POST /disponibilidades` e carregamento de opções de Profissionais; confirmar e cobrir os contratos sem chamadas de rede nos testes.
- Não prevê alteração do modelo de dados nem criação de endpoint. O Xano continua responsável por autenticação, autorização, persistência e conflitos.
- A ação fica disponível para Administração e Recepção, que podem cadastrar para qualquer Profissional ativo, conforme permissões já implementadas na API.
