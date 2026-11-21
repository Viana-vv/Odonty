## 1. Catálogo

- [x] 1.1 Criar GET `/procedimentos` autorizado para Administrador e Recepcionista e cliente estrito; verificar contratos Python e JavaScript sem rede.
- [x] 1.2 Liberar menu e tela para Recepcionista e isolar cache; verificar busca, lista vazia, atualização, sessão e navegação sem opções da Agenda.

## 2. Verificação

- [x] 2.1 Atualizar documentação e executar regressões e OpenSpec estrito.
- [x] 2.2 Publicar somente a rota nova após prévia e verificar acesso real administrativo sem alterar dados existentes.

## Verificacao em 21/11/2026

- Rotas publicadas no Xano: GET /procedimentos e GET /agenda/opcoes, depois de previa limitada a esses dois endpoints.
- Abertura das telas Home, Nova Consulta e Procedimentos confirmada com login real de Administrador e Recepcionista e chamadas REST reais, sem mocks e sem enviar agendamento.
- Regressoes executadas antes da orientacao de parar testes simulados: 319 testes Python e 7 subtestes aprovados, 52 testes JavaScript aprovados e validacao estrita OpenSpec sem erros. Nao foram acrescentadas novas execucoes simuladas apos essa orientacao.
- Alteracoes locais na main; dados existentes e historicos preservados.
