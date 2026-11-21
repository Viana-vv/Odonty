## 1. Correção

- [x] 1.1 Filtrar cadastros incompletos nas opções Xano e verificar contrato Python/JavaScript sem rede.

## 2. Verificação

- [x] 2.1 Executar regressões de Home, Agenda e Nova Consulta para os perfis administrativos e validar OpenSpec estrito.
- [x] 2.2 Publicar a rota após prévia e verificar Home e Nova Consulta com Administrador e Recepcionista e REST real, sem enviar agendamentos.

## Verificacao em 21/11/2026

- Rotas publicadas no Xano: GET /procedimentos e GET /agenda/opcoes, depois de previa limitada a esses dois endpoints.
- Abertura das telas Home, Nova Consulta e Procedimentos confirmada com login real de Administrador e Recepcionista e chamadas REST reais, sem mocks e sem enviar agendamento.
- Regressoes executadas antes da orientacao de parar testes simulados: 319 testes Python e 7 subtestes aprovados, 52 testes JavaScript aprovados e validacao estrita OpenSpec sem erros. Nao foram acrescentadas novas execucoes simuladas apos essa orientacao.
- Alteracoes locais na main; dados existentes e historicos preservados.
