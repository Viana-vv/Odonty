# Proposta: Corrigir envio do cadastro e atualizar a lista de Pacientes

## Problema

A rota interna `paciente` passa pelo fallback de módulos conectados em `paginas_equipe.renderizar`. Como não existe módulo Xano chamado `paciente`, o fallback redefine a navegação para `inicio`. O modal pode aparecer na primeira renderização, mas some no rerun que processaria o envio; assim, o POST não chega ao Xano e nenhum Paciente é criado. Após uma confirmação válida, a listagem também pode servir dados em cache e ocultar o novo cadastro.

## Escopo

- Preservar a rota `paciente` durante o ciclo de renderização do formulário e do POST.
- Invalidar os caches `pacientes` e `agenda/opcoes` somente após sucesso confirmado pelo cliente REST.
- Cobrir o retorno à lista com novo GET e exibição do Paciente criado.
- Preservar operação idempotente e dados pendentes em resultados incertos.

## Fora do escopo

- Alterar contrato REST, endpoint Xano, permissões, modelo de dados ou idempotência.
- Alterar outros fluxos/telas da equipe.

## Dependências e riscos

Dependência explícita: Issue #100 fornece `sorrisomais.cache_xano`; esta change integra a lista e o detalhe de Paciente a essa API de cache. a change deve ser integrada junto da implementação desse helper. A verificação em Xano deve usar somente contas e Pacientes fictícios, inativando os cadastros de teste e preservando o histórico do Prontuário.
