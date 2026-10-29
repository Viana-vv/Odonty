## Why

O formulário administrativo de cadastro de Profissional desaparecia durante reruns de edição, e respostas 429 para a lista de Especialidades podiam ser repetidas antes do prazo de espera. Isso interrompia o cadastro e ultrapassava o limite de chamadas permitido.

## What Changes

- Preservar a rota do cadastro e seus campos entre reruns.
- Respeitar a janela de espera de 20 segundos após resposta 429 de Especialidades.
- Manter a cache atual de Especialidades por sessão, sem prazo de expiração automático.

## Capabilities

### New Capabilities

### Modified Capabilities
- `cadastro-profissional`: preservar o formulário em reruns e aplicar espera após limite de requisições.

## Impact

Afeta a navegação Streamlit, estado de sessão do cadastro e testes unitários. Não altera APIs, payloads, Xano ou dependências.
