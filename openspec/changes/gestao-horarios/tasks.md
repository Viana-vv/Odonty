## 1. Contratos e autorização

- [x] 1.1 Confirmar GET e PATCH existentes, ajustar GET para incluir horários bloqueados futuros e preservar autenticação.
- [x] 1.2 Criar/manter testes Python e JavaScript separados por rota para GET e PATCH, sem rede.

## 2. Agenda

- [x] 2.1 Exibir Disponibilidades livres e bloqueadas para a data selecionada na Agenda, sem nova tela.
- [x] 2.2 Adicionar edição de intervalo, bloqueio e desbloqueio para perfis autorizados, exibindo retorno de sucesso, conflito e falha.
- [x] 2.3 Verificar controles da Agenda, isolamento da regra por perfil no Xano, estados vazios e manutenção do agendamento existente com interface Streamlit responsiva.

## 3. Verificação

- [x] 3.1 Executar testes Python, JavaScript e validação OpenSpec estrita.
- [x] 3.2 Verificar configuração para integração real: não executada porque apenas a URL base estava configurada; a ativação opt-in e as credenciais de metadados não estavam presentes. Nenhum segredo foi lido ou registrado.
