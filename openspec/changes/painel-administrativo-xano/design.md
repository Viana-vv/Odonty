## Context

Consulte `proposal.md` e `specs/interface-painel-administrativo/spec.md`. `renderizar_inicio` já distingue Administrador e Recepção; o painel da Recepção consome `listar_consultas` e não deve mudar nesta change. O cliente REST já oferece `listar_consultas` e `listar_opcoes_agenda`; a rota de opções retorna apenas ID e nome de Pacientes, Profissionais e Procedimentos ativos.

## Goals / Non-Goals

**Goals:**
- Manter a integração dentro da renderização existente do Streamlit.
- Derivar as métricas dos dados permitidos pelos contratos existentes e apresentar apenas campos mínimos.
- Preservar atalhos, navegação, identidade Sorriso Mais e comportamento dos outros perfis.

**Non-Goals:**
- Adicionar rotas, alterar contratos REST, sessão, autorização ou backend Xano.
- Reusar o resumo da Recepção ou alterar os painéis de Recepção e Profissional.

## Decisions

- No perfil Administrador, carregar Consultas do intervalo local de hoje por `listar_consultas(token, inicio, fim)` e cadastros ativos por `listar_opcoes_agenda(token)`. A contagem de Pacientes usa apenas o tamanho da lista de Pacientes; nenhum nome dessa lista é mostrado no painel. Não chamar `/agenda/opcoes` para Recepção, Profissional ou Paciente.
- Calcular Consultas hoje, realizadas e próxima Consulta a partir da lista retornada. Excluir Cancelada, Falta e Realizada da seleção da próxima Consulta. Ordenar pelo horário local e limitar a cinco itens exibidos.
- Tratar as duas leituras como uma operação do resumo: se alguma falhar, mostrar um único estado de erro e nenhum dado parcial. Tratar 401 e 403 com mensagens seguras e usar os mecanismos de sessão já existentes, sem mudar `sessao.py`.
- Compor os quatro cartões, agenda e atalhos conforme `02-visao-geral.png`, preservando componentes interativos do Streamlit. Não introduzir cache novo nesta change.
- Testar a interface usando cliente simulado e dados fictícios. Os testes não fazem chamadas de rede e não alteram os contratos REST.

## Risks / Trade-offs

- `GET /agenda/opcoes` retorna nomes que o resumo não precisa → manter a resposta apenas em memória durante a renderização e exibir exclusivamente a contagem de Pacientes ativos.
- As duas leituras podem refletir instantes diferentes → o resumo é informativo; a Agenda existente continua sendo a fonte para operações atuais.
- Uma falha em qualquer leitura torna todo o resumo indisponível → evitar indicadores parciais que pareçam representar uma fotografia consistente.

## Migration Plan

Não há alteração de backend, sessão, dados ou dependências. A reversão consiste em restaurar o painel administrativo anterior e remover os testes desta change.
