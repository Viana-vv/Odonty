## Contexto

Consulte `proposal.md` e `specs/registro-evolucao-clinica/spec.md`. O cliente já possui contratos para listar Consultas e Registros Clínicos e criar Registro Clínico. `POST /registros-clinicos` deriva o Profissional de `$auth.id`, exige Profissional ativo, verifica Paciente ativo e Prontuário ativo e, quando recebe `consulta_id`, valida que a Consulta corresponde ao Paciente e ao Profissional. A resposta não inclui a data nem o conteúdo do registro.

A rota de criação aceita apenas `paciente_id`, `conteudo`, `liberado_paciente` e `consulta_id` opcional. O contrato não suporta data do atendimento ou Procedimento. O endpoint GET de Consultas não aceita filtro específico de profissional em todos os perfis, mas o Xano retorna apenas o escopo autenticado para Profissionais.

## Objetivos e fora de escopo

**Objetivos:**
- Exibir um formulário de evolução integrado à área clínica e preservar o fluxo de histórico existente.
- Selecionar Paciente e Consulta a partir das Consultas já visíveis ao Profissional.
- Criar o Registro Clínico com o contrato atual e atualizar a linha do tempo após sucesso.
- Tratar sessão expirada, permissão negada, resposta inválida e indisponibilidade sem exibir conteúdo clínico em erros.

**Fora de escopo:**
- Alterar rotas, tabelas, exportações ou permissões Xano.
- Permitir escolher Profissional diferente da Conta de Acesso autenticada.
- Persistir data digitada, procedimento, diagnóstico estruturado ou status de liberação ao Paciente.

## Decis?es

- Implementar módulo Streamlit próprio acessível a partir de Prontuários, visível somente para `profissional`; o backend segue sendo a autoridade e retorna 403 para perfis sem permissão.
- Reutilizar GET `/consultas` para selecionar Paciente e Consulta e o POST existente para persistir. O Profissional exibido é o da sessão autenticada; não se envia `profissional_id`.
- Usar um formulário em uma coluna com Paciente, Consulta opcional e campo de texto longo para evolução/observações, seguindo a hierarquia, paleta e espaçamento da referência. Mostrar a data atual do sistema apenas como informativa se necessário, sem coletá-la nem enviá-la.
- Não exibir Procedimento como campo gravável, pois não há campo no contrato e a relação de procedimento com Consulta já possui fluxo próprio.
- Após POST confirmado, limpar o cache clínico da sessão e rerun para que GET do histórico confirme a persistência. Não repetir automaticamente o POST em falha ambígua.
- Criar/estender testes de contrato por rota apenas se for necessário; cada chamada GET/POST terá um teste Python e um JavaScript. As chamadas ficam mockadas nos testes unitários.

## Riscos e compensa??es

- [O endpoint GET pode retornar muitas Consultas] → reutilizar a resposta já carregada/cached no histórico da sessão e limitar seleções às Consultas retornadas pelo Xano.
- [Um POST pode ter sucesso no backend e a resposta se perder] → informar falha de confirmação e não reenviar automaticamente; permitir nova tentativa deliberada após recarga.
- [Referência visual contém campos fora do contrato] → omitir data editável e Procedimento em vez de apresentar entradas que seriam ignoradas.

## Plano de migra??o

Nenhuma migração de dados ou implantação Xano é necessária. Publicar a aplicação Streamlit com o módulo de tela e seus testes. Rollback: remover a navegação e o módulo; os Registros Clínicos criados permanecem como histórico.
