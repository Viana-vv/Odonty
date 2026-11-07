## Why

As listas do sistema só refletem alterações feitas por outra sessão depois de uma atualização manual. A aplicação precisa consultar novamente os dados periodicamente, sem substituir a invalidação imediata já usada após mutações.

## What Changes

- Atualizar periodicamente os dados autenticados da tela, respeitando a sessão atual.
- Invalidar o cache privado antes da atualização automática para buscar dados atuais no Xano.
- Não interromper formulários ou fluxos de edição em andamento.
- Manter o botão de atualização manual e os contratos REST existentes.

## Capabilities

### New Capabilities

### Modified Capabilities

- `cache-leituras`: permitir atualização periódica das leituras autenticadas sem compartilhar dados entre sessões.
- `acesso-autenticado`: manter a sessão e a autorização durante a atualização automática.

## Impact

- `app.py` e `sorrisomais/cache_xano.py`.
- Testes de sessão, cache e interface.
- Nenhuma alteração no Xano ou em contratos REST.
