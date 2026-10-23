## Contexto

Consulte `proposal.md` e `specs/interface-painel-profissional/spec.md`. `sorrisomais/painel_profissional.py` já lê as Consultas do dia pela API. `sorrisomais/paginas_equipe.py` oferece `_carregar_consultas_agenda`, cacheada por Conta de Acesso, data local e vinte segundos; a função reutiliza o contrato `ClienteXano.listar_consultas` e o cache é removido no logout. A referência aprovada está em `sorriso-mais-kit-recriacao/sorriso-mais-kit-recriacao/referencias-telas/15-painel-dentista.png`.

## Objetivos / Não objetivos

**Objetivos:**

- Ajustar a composição do painel à referência, mantendo componentes interativos e responsivos do Streamlit.
- Reaproveitar o cache existente da Agenda e derivar indicadores e linhas da mesma resposta autorizada.
- Manter mensagens seguras e não renderizar conteúdo clínico nem detalhes da API.

**Não objetivos:**

- Criar outro cache, endpoint ou filtro local de Profissional.
- Alterar operações de Consulta, permissões, Xano, contratos REST ou o comportamento dos outros perfis.
- Consultar dados de Pacientes ativos em `/agenda/opcoes`.

## Decisões

- Em `painel_profissional.renderizar`, usar a data de `America/Sao_Paulo` e chamar o helper diário de cache da Agenda em `paginas_equipe.py`. O helper já agrupa por hash da credencial e data, expira em vinte segundos, bloqueia tentativas após erro e é limpo no logout. Alternativa considerada: duplicar o mecanismo no painel; descartada para evitar duas políticas de expiração e invalidação para as mesmas Consultas.
- Continuar chamando `listar_consultas` sem `profissional_id`: o Xano controla o escopo da Conta de Acesso. A interface ordena e apresenta a resposta recebida, sem tentar substituir a autorização do servidor.
- Calcular Consultas do dia, Realizadas, Confirmadas e próxima Consulta a partir de `situacao` e `inicio_em`; considerar a próxima Consulta apenas se for futura e não estiver Realizada, Cancelada ou em Falta. Converter a situação legada `Concluída` para `Realizada` somente para exibição.
- Renderizar quatro cartões no topo; abaixo, organizar lista com até cinco linhas no painel maior e os atalhos existentes de Agenda e Prontuários na coluna lateral. Usar nome do Paciente, horário e situação, omitindo Procedimentos, motivos, contatos e campos clínicos. No celular, empilhar lista e atalhos sem perder botões.
- Manter erro genérico e botão de nova tentativa para falhas recuperáveis. Para HTTP 401, limpar a sessão como já faz a tela; para 403, informar a falta de permissão sem detalhes técnicos. Uma falha de estrutura de resposta também produz estado de erro, sem converter dados inválidos em lista vazia.
- Aplicar classes CSS específicas com os tokens já definidos em `assets/estilos.css`; não depender de imagens da referência nem de recursos externos.

## Riscos / Compensações

- O cache compartilhado com a Agenda pode refletir uma mudança feita por outra Conta de Acesso por até vinte segundos → preservar o TTL já adotado e depender da leitura autorizada do Xano ao expirar.
- Valores inesperados no nome do Paciente ou situação podem desorganizar a linha → usar texto renderizado pelo Streamlit e validar os campos mínimos antes de apresentar os indicadores.
- Largura estreita pode comprimir as quatro métricas → usar CSS responsivo para reduzir a grade e empilhar os painéis abaixo do breakpoint existente.

## Plano de migração

Não há migração de dados nem mudança de API. Reverter o refinamento requer restaurar `painel_profissional.py`, os estilos específicos e os testes correspondentes.
