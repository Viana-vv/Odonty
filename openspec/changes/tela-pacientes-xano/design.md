## Context

A proposta e os requisitos estão em `proposal.md` e `specs/interface-pacientes/spec.md`. O modo conectado usa módulos Streamlit por área e o cliente existente valida a resposta de `listar_opcoes_agenda`; esta change não altera integração ou autorização no Xano.

## Goals / Non-Goals

**Goals:** compor uma tela responsiva inspirada na hierarquia visual da referência aprovada, adaptada aos campos mínimos do contrato existente; isolar a renderização em um módulo próprio.

**Non-Goals:** mudar o menu compartilhado ou o roteamento central; ampliar o contrato da API; criar operações de cadastro, edição, inativação ou consulta de detalhes.

## Decisions

- A tela chamará somente `cliente.listar_opcoes_agenda(token)` e consumirá o grupo `pacientes`, mantendo o cliente responsável pela validação do contrato. Uma rota exclusiva de listagem exigiria mudança de backend fora do escopo autorizado.
- A referência contém campos que a rota não retorna. A tabela será simplificada para identificador e nome, com busca somente pelo nome; não haverá placeholders nem chamadas a outras rotas.
- A função de renderização ficará em `sorrisomais/pagina_pacientes_xano.py`; o roteamento será integrado pela coordenação em arquivos compartilhados.
- Os testes de UI simularão o cliente e a sessão Streamlit; nenhuma requisição real de rede será realizada.

## Risks / Trade-offs

- A rota de opções também fornece dados de Profissionais e Procedimentos; o cliente valida esses grupos como parte do contrato. A tela usa somente `pacientes` e não altera a rota.
- Como a API retorna somente registros elegíveis e não permite paginação, a busca é local sobre os itens recebidos; a interface não promete busca em campos ausentes.
- A coordenação precisa conectar o novo módulo à navegação; até essa integração, a função isolada não será acessível pelo menu.
