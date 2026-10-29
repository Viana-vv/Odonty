## Context

Ver `proposal.md`. A rota GET existente autoriza a Conta de Acesso e retorna os registros dentro do escopo, mas não retorna as linhas append-only de `registro_clinico_retificacao`.

## Goals / Non-Goals

- Enriquecer a resposta clínica somente com retificações relacionadas ao registro já autorizado.
- Preservar autorização, resposta `no-store` e `history = false`.
- Não adicionar endpoint separado, permissões administrativas clínicas, nem edição destrutiva.

## Decisions

- Anexar `retificacoes` no item da resposta de `GET /registros-clinicos`, consultando pelo ID do registro já filtrado por escopo. Isso mantém a autorização centralizada no GET e reduz chamadas externas.
- Ordenar por `criada_em` ascendente e retornar `id`, `profissional_id`, `conteudo`, `justificativa` e `criada_em`; não inferir o nome do profissional.
- Exibir a trilha abaixo do conteúdo original usando apenas campos retornados. O filtro visual não altera o escopo do Xano.
- Manter a seleção de Paciente fora do formulário de envio para que o Streamlit atualize imediatamente as Consultas dependentes. Na troca de Paciente, limpar Consulta e conteúdo anteriores para evitar associar texto ao Prontuário incorreto.
- Inicializar a seleção com o filtro do Prontuário, limpar o rascunho em callbacks de fechar/cancelar e após confirmação, e remover os estados clínicos na limpeza da sessão. Após expiração no POST, interromper também a apresentação do histórico na tela chamadora.
- Renderizar o formulário na área principal, preservando o contêiner e a hierarquia visual existentes; a coluna estreita de ações não deve conter o formulário inteiro. Um contêiner substituível permite remover imediatamente os campos clínicos quando o POST retorna HTTP 401.
- Alternativas: rota separada exigiria outra chamada e nova superfície de autorização; substituir o original pela última versão destruiria a trilha, portanto ambas foram descartadas.

## Risks / Trade-offs

- [P2: custo N+1 ao consultar retificações] → o GET executa uma consulta interna de retificações para cada Registro Clínico incluído; a consulta permanece limitada a registros autorizados e a tabela possui índice por `registro_clinico_id`. Não foi possível confirmar no código ou nos testes existentes a sintaxe Xano para buscar por uma lista de IDs, então não se introduziu uma consulta em lote presumida. Reavaliar quando houver sintaxe validada e teste no grupo publicado; considerar paginação se o volume crescer.
- [Grupo publicado diverge do export local] → não considerar deploy validado até testar a rota e permissões no Xano publicado.

## Migration Plan

Nenhuma migração de dados. Publicar export atualizado da rota GET, confirmar permissões e contratos no grupo Xano com contas e dados fictícios. Rollback: restaurar export anterior da rota; retificações persistidas permanecem intactas.
