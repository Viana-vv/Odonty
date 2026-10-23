## Context

A Agenda já concentra consultas e cadastro de Disponibilidades. O cliente possui `listar_disponibilidades` e `atualizar_disponibilidade`; o endpoint PATCH no Xano verifica perfil, escopo do Profissional, estado futuro e conflitos transacionais. O GET existente omite horários bloqueados, então precisa incluí-los para viabilizar desbloqueio. A referência visual aprovada é `03-agenda.png` do kit Sorriso Mais.

## Goals / Non-Goals

**Goals:**
- Mostrar e manter horários no contexto da Agenda e da data selecionada.
- Atualizar a visualização somente após resposta bem-sucedida do Xano.
- Deixar autorização e conflitos sob responsabilidade do backend.

**Non-Goals:**
- Criar página separada ou outro cadastro de horários.
- Alterar consulta, persistência, tabelas ou regras de conflito.
- Permitir alteração de horários reservados, indisponíveis ou passados.

## Decisions

- Reutilizar GET `/disponibilidades` com `inicio` e `fim` para o dia selecionado e PATCH `/disponibilidades/{id}` para intervalo e situação. Nenhuma rota nova é necessária.
- Ajustar o filtro do GET no export Xano para listar apenas situações `disponivel` e `bloqueado` e manter o limite de horários futuros. As permissões de leitura continuam exigindo sessão válida; a escrita preserva permissões e restrição do Profissional já implementadas no PATCH.
- Colocar uma seção compacta de horários abaixo dos filtros da Agenda, seguindo cores, hierarquia e espaçamento da referência 03. As ações só aparecem para perfis autorizados e dependem da autorização do Xano.
- Reutilizar por vinte segundos a leitura dos horários da mesma data e sessão, evitando uma chamada GET a cada rerun do Streamlit; invalidar o cache após edição, bloqueio, desbloqueio, agendamento ou cadastro de horário.
- Após PATCH bem-sucedido, invalidar leituras em cache e carregar a Agenda novamente; após erro, conservar a situação e mostrar mensagem segura.
- Testar a interface e contrato com respostas simuladas; nenhum teste unitário envia chamadas de rede.

## Risks / Trade-offs

- A lista reflete a leitura da API e pode envelhecer por concorrência externa; o PATCH valida o estado atual e retorna conflito sem aceitar alteração indevida.
- O GET já é acessível a contas autenticadas; incluir situação de bloqueio é dado administrativo de Agenda e não expõe informação clínica.
- A referência visual é para a Agenda geral; usar seus padrões de composição sem alterar a estrutura de navegação.

## Migration Plan

Sem migração de dados. Publicar a alteração do GET no Xano e então a interface Streamlit. Rollback consiste em retirar a seção da Agenda e restaurar o filtro anterior do GET.
