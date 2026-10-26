## Contexto

Exames, Reagendamento e Procedimentos da Consulta foram implementados em módulos separados. A navegação principal da equipe usa uma lista declarativa de áreas, checa disponibilidade do módulo e chama interfaces com assinatura uniforme; Procedimentos da Consulta é a exceção porque precisa receber uma Consulta. Esta change integra os módulos existentes sem alterar clientes REST, regras de negócio ou o portal do Paciente da Issue #84.

## Objetivos e não objetivos

**Objetivos:** permitir acesso por perfil autorizado; reutilizar as interfaces e clientes existentes; passar Consulta explicitamente para Procedimentos da Consulta; garantir fallback para rota inválida, módulo ausente e contexto ausente; manter o catálogo administrativo separado.

**Não objetivos:** alterar endpoints ou autorização Xano; mudar os fluxos internos das telas; criar novo portal de Paciente; permitir acesso administrativo a dados clínicos.

## Decisões

- `navegacao.py` permanece fonte das áreas, perfis, módulos e regras de roteamento. As áreas novas usarão os nomes de rota distintos do catálogo: Reagendamento e Procedimentos da Consulta não reutilizam a chave `procedimentos` do catálogo.
- Exames será roteado para o módulo existente e receberá `(cliente, conta)`. Os perfis serão limitados ao que a interface/contrato existente oferece à equipe: Profissional. O entrypoint próprio do Paciente da Issue #84 não será tocado nem acoplado aqui.
- Reagendamento será uma rota da equipe para Administrador e Recepcionista. O renderer existente já valida o perfil e o Xano continua sendo a autoridade final.
- Procedimentos da Consulta será uma ação contextual na Consulta apresentada ao Profissional. `paginas_equipe.py` armazena somente a seleção de interface em `st.session_state`; o dispatcher valida que o valor é uma Consulta com identificador inteiro e passa o objeto selecionado a `renderizar(cliente, conta, consulta)`. Troca de Consulta, saída da rota e sessão/perfil inválido limpam o contexto.
- Entrada direta em rota sem contexto não usa dados inventados nem executa GET/PATCH; apresenta orientação e link de retorno à Agenda.
- A disponibilidade de módulos usa o mecanismo existente. Importação ou renderer inválido deve falhar fechado, com aviso seguro.
- Os testes usarão clientes e módulos simulados, sem chamadas à rede, cobrindo perfis permitidos/negados, rota direta, contexto correto e fallback.

## Riscos e compensações

- A agenda atual pode não expor uma seleção de Consulta adequada para o Profissional; o ponto de entrada deve reutilizar o cartão/linha já existente e fornecer exatamente seu objeto, sem criar um novo fluxo de busca clínica.
- Estado de sessão pode sobreviver a reruns; limpar o contexto ao trocar de área/Consulta evita associação incorreta.
- Esconder rotas não constitui autorização. Os clientes continuam chamando APIs que verificam perfil e escopo no Xano.

## Plano de implementação

1. Adicionar definições de área/módulo/perfil e testes das regras em `navegacao.py`.
2. Adicionar entradas de menu e dispatch para Exames e Reagendamento, com testes de abertura e perfis.
3. Conectar ação contextual de Procedimentos da Consulta no fluxo do Profissional, validando e limpando o estado de seleção; cobrir passagem e ausência de contexto.
4. Executar testes focados de navegação e regressão da agenda/equipe, além de `openspec validate integrar-telas-orfas --strict` e `git diff --check`.

## Questões em aberto

Nenhuma. O ponto de entrada contextual deve usar a Consulta já disponível na agenda do Profissional, conforme os limites desta change.
