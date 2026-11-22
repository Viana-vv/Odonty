## 1. Contratos e persistência

- [x] 1.1 Definir e implementar POST/PATCH de Procedimentos no Xano, permitindo POST para Administrador, Recepcionista e Profissional; restringir PATCH e inativação a Administrador e Recepcionista.
- [x] 1.2 Definir e implementar POST/PATCH de ConsultaProcedimento no Xano, com autorização do Profissional e preservação histórica.
- [ ] 1.3 Atualizar o cliente Python e criar testes unitários Python e JavaScript separados para cada rota GET/POST/PATCH afetada, sem rede real.

## 2. Catálogo administrativo

- [x] 2.1 Atualizar a tela de Procedimentos com cadastro para os três perfis, edição/inativação para equipe administrativa, filtro por situação e mensagens de erro.
- [x] 2.2 Garantir que Administrador, Recepcionista e Profissional possam criar e que somente Administrador e Recepcionista possam editar ou inativar.

## 3. Atendimento profissional

- [x] 3.1 Atualizar Procedimentos da Consulta para adicionar Procedimento ativo à Consulta autorizada.
- [x] 3.2 Implementar as ações de realizado e cancelado com responsável, data e histórico.
- [x] 3.3 Preservar a seleção de Procedimentos ativos no agendamento administrativo e exibir vínculos históricos inativos.

## 4. Verificação e documentação

- [x] 4.1 Atualizar documentação de domínio, permissões e fluxo visual.
- [ ] 4.2 Verificar sucesso, validações, duplicidade, sessão expirada, falta de permissão, erro da API e retorno visual após cada operação.
