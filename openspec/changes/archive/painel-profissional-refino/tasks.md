## 1. Resumo do Profissional

- [x] 1.1 Reutilizar a leitura e o cache diário da Agenda no painel do Profissional sem acrescentar filtros de escopo no frontend; verificar que a Conta de Acesso e a data são respeitadas em testes simulados.
- [x] 1.2 Organizar quatro métricas e uma agenda ordenada com no máximo cinco itens, omitindo campos clínicos, contatos e motivos; verificar contagens, próxima Consulta, limite e estados vazio/resposta inválida com dados fictícios.
- [x] 1.3 Tratar sessão expirada, acesso recusado e falhas recuperáveis com mensagens seguras, limpeza de sessão e nova tentativa existente; verificar que nenhuma Consulta antiga ou mensagem técnica aparece após erro.
- [x] 1.4 Aplicar cartões e lista responsivos conforme a referência 15, mantendo atalhos existentes de Agenda e Prontuários; verificar chaves, destinos e estilos específicos em testes de interface e inspeção local.

## 2. Verificação e revisão

- [x] 2.1 Executar testes do painel e da Agenda com clientes simulados, sem chamadas reais de rede; verificar cache de vinte segundos, troca de Conta de Acesso e estados de erro.
- [x] 2.2 Executar `openspec validate painel-profissional-refino --strict` e `git diff --check`; conferir ausência de alteração de contratos e de dados ou credenciais reais.
