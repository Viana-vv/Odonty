## Why

Na largura de tablet de 768 px, a Agenda e os atalhos do painel do Profissional continuam lado a lado, deixando o botão “Ver agenda completa” sem espaço para seu rótulo completo. A captura evidencia desvio do padrão responsivo aprovado para as telas da equipe.

## What Changes

- Ajustar o painel do Profissional para empilhar a Agenda e os atalhos nas larguras em que a composição atual comprime o cabeçalho da Agenda.
- Manter a composição lado a lado em desktop e em celular, preservar as ações e evitar rolagem horizontal.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `interface-equipe`: esclarecer a adaptação responsiva do painel do Profissional em larguras de tablet.

## Impact

- `sorrisomais/painel_profissional.py` e, se necessário, regras de estilo existentes do painel em `assets/estilos.css`.
- Testes de interface do painel Profissional.
- Sem alterações em API, autenticação, autorização, dados ou regras de negócio.
