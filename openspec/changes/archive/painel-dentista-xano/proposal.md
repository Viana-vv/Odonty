## Why

O perfil Profissional ainda não possui uma visão inicial integrada ao Xano que reúna suas Consultas do dia e os acessos de trabalho mais usados. O painel deve refletir a agenda autorizada pelo backend sem criar dados demonstrativos ou expor informações clínicas em resumos.

## What Changes

- Criar a visão geral do Profissional usando o contrato Xano existente de listagem de Consultas.
- Apresentar indicadores derivados das Consultas retornadas, lista do dia e acesso à Agenda e ao Prontuário.
- Aplicar a hierarquia visual da referência `15-painel-dentista.png`.
- Tratar sessão inválida, acesso negado, falha de API e resposta vazia com mensagens seguras.

## Capabilities

### New Capabilities
- `painel-profissional`: visão geral autenticada da agenda diária do Profissional.

### Modified Capabilities
Nenhuma.

## Impact

- Streamlit: navegação e página inicial do perfil Profissional.
- Xano: somente o contrato existente de listagem de Consultas; nenhuma rota ou dado novo.
- Testes unitários Python e JavaScript para cada contrato GET efetivamente usado, sem rede.

## Fora de escopo

- Criar, alterar ou inventar endpoints Xano.
- Agendar Consultas, administrar disponibilidades ou alterar sua situação nesta visão.
- Exibir ou editar conteúdo clínico na lista/resumo do dashboard.
- Métricas de Pacientes ativos ou contagens que não possam ser derivadas dos contratos disponíveis.
