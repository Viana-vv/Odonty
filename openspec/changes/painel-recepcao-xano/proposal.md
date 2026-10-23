## Why

A Recepção abre a Visão geral conectada, mas hoje recebe apenas uma apresentação genérica sem resumo operacional do dia. O painel deve ajudá-la a acompanhar a agenda diária e localizar rapidamente a próxima Consulta usando os dados administrativos já autorizados pelo Xano.

## What Changes

- Exibir para a Recepção um resumo conectado do dia com total de Consultas, Consultas realizadas, próxima Consulta ativa e até cinco Consultas ordenadas por horário.
- Reutilizar `GET /consultas`, respeitar o escopo já aplicado pelo Xano e apresentar estados vazios, falhas e sessão expirada sem manter dados antigos como atuais.
- Aplicar a composição visual da referência aprovada `14-painel-recepcao.png`, mantendo atalhos somente para áreas já funcionais e autorizadas.
- Não adicionar contratos, rotas, consultas extras de cadastros ou dados clínicos ao painel.

Fora do escopo: painel de Administrador ou Profissional, métricas de Pacientes ativos, ações de agendamento ou alteração de Consulta dentro do painel, alterações no Xano e qualquer dado clínico ou de contato.

## Capabilities

### New Capabilities

- `interface-painel-recepcao`: resumo diário conectado para a Recepção baseado no contrato existente de Consultas e sem conteúdo clínico.

### Modified Capabilities

Nenhuma.

## Impact

- Streamlit: renderização da Visão geral conectada em `sorrisomais/paginas_equipe.py` e testes unitários de interface.
- API: reutilização do cliente existente `ClienteXano.listar_consultas` com filtro de data; nenhum contrato REST novo ou alterado.
- Xano: nenhuma alteração de rota, tabela ou permissão; a autorização e o escopo existentes em `GET /consultas` permanecem sob controle do Xano.
- Verificação: testes de interface com cliente simulado, sem rede, e validação OpenSpec. A inspeção visual usa dados fictícios.
