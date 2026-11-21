## Why

Um Profissional ativo sem nome, CRO e especialidade válida bloqueia a listagem administrativa e as opções usadas por Reagendar Consulta. A Recepcionista recebe um erro genérico em ambas as telas, mesmo com outros cadastros válidos.

## What Changes

- Representar campos cadastrais vazios e especialidade ausente na listagem como cadastro incompleto, preservando identificador, situação e autorização.
- Carregar Pacientes e Profissionais por suas rotas próprias no reagendamento, sem depender de Procedimentos ou das opções da Agenda.
- Oferecer somente Profissionais ativos com cadastro completo no seletor de destino.
- Preservar controles por perfil, validação de dados malformados, reservas e histórico. Não alterar cadastros existentes nem regras de persistência de reagendamento.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `gestao-profissionais`: apresentar cadastro incompleto sem impedir leitura dos demais.
- `reagendamento-consulta`: carregar seleções independentemente das opções da Agenda e impedir escolha de cadastro incompleto.

## Impact

GET `/profissionais` no Xano, cliente REST, duas telas Streamlit, contratos Python/JavaScript e regressões de interface. Sem alteração de tabelas ou registros. Trabalho local na `main` autorizado explicitamente pelo usuário.
