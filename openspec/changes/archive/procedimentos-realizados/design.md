## Context

A tabela `consulta_procedimento` representa os vínculos N:N e já guarda `profissional_id` e `criado_em` do vínculo feito ao agendar. Esses campos são valores históricos do planejamento. A autorização deve ser aplicada pelas APIs Xano; a nova tela e o cliente ficarão em módulos dedicados, sem editar arquivos de navegação existentes.

## Goals / Non-Goals

**Goals:**
- Acrescentar situação com padrão `planejado` e campos independentes `realizado_por_profissional_id` e `realizado_em`.
- Expor um GET de vínculos no escopo do Profissional e um PATCH atômico que realiza somente vínculo planejado da sua própria Consulta.
- Criar página Streamlit independente e cliente REST dedicado.
- Manter dados do planejamento e registros existentes.

**Non-Goals:**
- Desfazer, retificar ou excluir realização.
- Mudança em Consulta, prontuário, pagamento ou autorização de outros perfis.
- Integração na navegação principal, que ficará a cargo do agente principal.

## Decisions

- A nova situação é aditiva e enumera `planejado`, `autorizado`, `realizado` e `cancelado`, seguindo o domínio. Para esta operação só é permitido `planejado` → `realizado`; os outros estados não são gravados por estas rotas.
- `profissional_id` e `criado_em` permanecem imutáveis como dados do vínculo planejado. A conclusão preenche apenas `realizado_por_profissional_id` e `realizado_em`, utilizando o profissional autenticado e `now` do Xano.
- Criar `GET /consultas/{id}/procedimentos` e `PATCH /consultas/{id}/procedimentos/{consulta_procedimento_id}/realizacao`. O PATCH valida sessão ativa, perfil Profissional e escopo da Consulta, então atualiza a linha de `agenda_controle` do Profissional dentro da transação e relê o vínculo antes de validar `planejado` e gravar. A chave única de escopo/identificador arbitra a criação inicial da trava; repetição ou concorrência perdedora retorna conflito. Consulta ou vínculo fora do escopo não deve ser distinguível de inexistente.
- Para registros existentes, a migration deve aplicar `situacao=planejado`, preservando todos os outros valores. A migration só será considerada segura depois de verificada em grupo Xano temporário; nenhuma mutação será feita no grupo de produção.
- A interface usa Streamlit e segue a hierarquia da referência 13 (histórico em cartões) e os controles da referência 08 (campos e botões claros), dentro de uma nova página/módulo. Não há dependência nova.
- Testes de contrato são isolados e simulam a camada HTTP, com um arquivo Python e um JavaScript por rota; os testes não acessam rede. Os testes de tela também simulam os retornos do cliente.

## Risks / Trade-offs

- A aplicação do valor padrão aos vínculos já persistidos pode variar conforme a migration de schema do Xano → validar no grupo temporário antes de usar qualquer export atualizado.
- Duas tentativas concorrentes podem disputar o mesmo vínculo → serializar por linha `agenda_controle` do Profissional e revalidar situação após adquirir a trava; a primeira criação da linha é arbitrada pelo índice único existente.
- A página isolada não fica acessível pela navegação até a integração posterior → documentar a função pública de renderização para o agente principal.
- O grupo temporário pode não estar disponível nesta execução → interromper a validação Xano e reportar; não apontar para credenciais de produção.

## Migration Plan

1. No grupo Xano temporário, adicionar a situação com valor padrão planejado e os dois campos nullable, verificando que vínculos existentes ficam planejados e os campos de realização vazios, sem perder autoria/data do vínculo.
2. Publicar e exercitar as rotas no grupo temporário com casos de sucesso, fora do escopo, repetição, usuário não profissional e vínculos ausentes, respeitando ao menos 3 segundos entre requisições.
3. Só então considerar os exports compatíveis; a promoção para produção requer ação posterior fora desta tarefa. Em rollback, retirar as rotas e manter campos aditivos e dados gravados; não apagar histórico.
