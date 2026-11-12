## Why

A recarga do navegador perde o estado da conexão Streamlit e exige novo login mesmo com sessão válida no Xano.

## What Changes

- Recuperar a sessão local por identificador aleatório em cookie HttpOnly.
- Guardar a credencial somente na memória do processo Python, limitada à validade do Xano.
- Oferecer inicializador local e ativação explícita no navegador após login.
- Invalidar a recuperação ao sair e revalidar a identidade no Xano após recarga.

## Capabilities

### New Capabilities
- `sessao-local`: recuperação de sessão após recarga em localhost.

### Modified Capabilities

## Impact

Streamlit, estado de sessão e inicialização local. Sem alteração de contratos REST ou de autorização no Xano.
