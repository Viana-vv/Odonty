# Sorriso+ — Kit de referências para começar do zero

**Revisado em 30/09/2026. Leia este arquivo primeiro.**

Este pacote foi preparado para o grupo recriar o Sorriso+, um sistema acadêmico de gestão odontológica, em um novo projeto no VS Code. Ele pode ser compartilhado entre os integrantes sem acesso ao chat, ao computador ou à conta de quem criou o protótipo.

## 1. O que este ZIP contém

```text
sorriso-mais-kit-recriacao/
├── README.md
├── docs/
│   └── especificacao-telas-para-agente-vscode.md
└── referencias-telas/
    ├── 01-login.png
    ├── 02-visao-geral.png
    ├── 03-agenda.png
    ├── 04-pacientes.png
    ├── 05-profissionais.png
    ├── 06-prontuarios.png
    ├── 07-procedimentos.png
    ├── 08-nova-consulta.png
    ├── 09-novo-paciente.png
    ├── 10-novo-profissional.png
    ├── 11-nova-evolucao.png
    ├── 12-editar-paciente.png
    ├── 13-prontuario-individual.png
    ├── 14-painel-recepcao.png
    └── 15-painel-dentista.png
```

- [Especificação completa](docs/especificacao-telas-para-agente-vscode.md): funcionamento de cada tela, campos, permissões, justificativas, limitações e testes.
- [Pasta de prints](referencias-telas/): aparência de referência das telas, formulários e variações por perfil.
- Este README: como preparar o trabalho, instruir o agente e colaborar.

**Este ZIP não é um aplicativo executável.** Não contém código da aplicação antiga, dependências instaladas, banco exportado, configuração do Xano, tokens, repositório GitHub ou configuração pronta do OpenSpec. Não há comando para “rodar o ZIP”: primeiro vocês vão criar o novo projeto com apoio das referências.

O material é suficiente para iniciar a reconstrução de telas e fluxos. O enunciado do professor e os contratos da API serão necessários para validar, respectivamente, os requisitos acadêmicos e a integração final. Nenhum deles foi incluído no pacote.

## 2. O que vamos recriar

São sete telas principais: Login, Visão geral, Agenda, Pacientes, Profissionais, Prontuários e Procedimentos. Os demais prints são formulários, prontuário filtrado ou variações de perfil — não são módulos extras.

O objetivo é reproduzir o produto já desenhado: aparência próxima, mesma organização, informações equivalentes e fluxos descritos na especificação. Não inventar um novo sistema, redesign completo ou funcionalidades adicionais.

A documentação anterior definiu **Python + Streamlit no frontend e Xano no backend**, usando OpenSpec para organizar mudanças. Confirmem essa decisão com o grupo e com o enunciado antes da implementação. O protótipo antigo foi feito em React/Vinext; suas imagens não garantem reprodução pixel a pixel usando componentes Streamlit.

Se a exigência do grupo for igualdade visual absoluta, discutam essa escolha antes de começar. Não deixem cada integrante ou agente escolher uma tecnologia diferente por conta própria.

## 3. Como abrir e organizar no VS Code

1. Baixe e extraia o ZIP; não trabalhe dentro do arquivo compactado.
2. Crie uma pasta nova para o projeto, por exemplo `sorriso-mais`.
3. Dentro dela, crie `referencias/` e copie a pasta inteira `sorriso-mais-kit-recriacao` para esse local.
4. Abra **a pasta do projeto `sorriso-mais`** no VS Code, não apenas uma imagem ou documento isolado.
5. Abra `referencias/sorriso-mais-kit-recriacao/README.md` e leia este guia.
6. Abra o arquivo de especificação. Arquivos `.md` são textos comuns; podem ser lidos diretamente ou pela prévia de Markdown do editor.
7. Abra os PNGs no editor ou no visualizador de imagens do computador para compará-los.
8. Mantenha os arquivos do aplicativo separados da pasta de referências. Não implemente o sistema dentro de `referencias-telas/`.

O resultado inicial será:

```text
sorriso-mais/                         ← abrir esta pasta no VS Code
└── referencias/
    └── sorriso-mais-kit-recriacao/   ← este pacote, preservado
```

Os arquivos de código, testes, dependências e OpenSpec serão criados depois, na estrutura aprovada pelo grupo. Não é preciso copiar nenhum arquivo antigo do computador do autor do protótipo.

## 4. Como fornecer contexto ao agente

Um agente novo não conhece a conversa anterior. Não escreva apenas “faça igual ao Sorriso+” ou “continue o que já fizemos”. Forneça os arquivos e o objetivo explicitamente.

Se o agente puder ler a pasta de trabalho, indique os caminhos abaixo. Se ele depender de anexos, anexe primeiro o README e a especificação; depois, os prints relevantes para cada etapa. Não presuma que o agente consegue ver todas as imagens apenas porque estão na pasta: peça que informe quais abriu.

### Mensagem inicial pronta para copiar

```text
Vamos recriar do zero o Sorriso+, nosso projeto acadêmico de gestão
odontológica. O objetivo é reproduzir as telas e os fluxos das referências,
sem redesenhar o produto nem acrescentar módulos.

Leia integralmente:
1. referencias/sorriso-mais-kit-recriacao/README.md
2. referencias/sorriso-mais-kit-recriacao/docs/especificacao-telas-para-agente-vscode.md

Inspecione as imagens em:
referencias/sorriso-mais-kit-recriacao/referencias-telas/

Não temos código anterior neste ambiente. Não dependa do chat ou do site
original, de caminhos de outra máquina ou de arquivos não fornecidos.

A direção técnica registrada é Python + Streamlit e backend Xano, com
OpenSpec e documentação em português. Primeiro confirme o contexto do
ambiente e apresente o planejamento; não instale dependências ou implemente
todas as partes nesta primeira resposta.

Separe duas etapas: (A) recriação demonstrativa das telas e fluxos com dados
fictícios; (B) integração real ao Xano, depois de termos contratos e acesso
autorizado. A falta do Xano não deve bloquear a etapa A. Não trate login
simulado ou dados de sessão como autenticação/persistência reais.

Explique: arquivos lidos, entendimento das telas, diferenças entre protótipo
e alvo, estrutura proposta, primeira mudança pequena e critérios de teste.
Use as ressalvas dos prints: o destaque do menu deve corresponder à tela
atual, mesmo quando a captura antiga mostrar outro item selecionado.

Não crie banco, não publique e não altere serviços externos. Não solicite
senhas pessoais. Aguarde nossa aprovação da primeira etapa.
```

Se vocês escolherem outra posição para o pacote, ajustem os três caminhos da mensagem antes de enviá-la.

## 5. Antes de autorizar a primeira implementação

Confiram se o agente:

- reconheceu sete telas principais, e não 15 módulos;
- entendeu os três perfis e não deu as mesmas ações a todos;
- manteve o tema odontológico, as cores e a organização das referências;
- separou recriação demonstrativa de integração;
- não afirmou que o Xano já está conectado;
- não acrescentou financeiro, estoque, exames ou outros módulos fora do escopo;
- propôs etapas pequenas e testáveis;
- identificou a stack sem trocar de tecnologia silenciosamente;
- não exige os arquivos do projeto antigo para começar.

Se houver divergência, corrijam o plano antes de pedir código. O texto da especificação prevalece sobre inconsistências visuais conhecidas dos prints. Requisitos do professor e decisões novas do grupo devem ser registrados e reconciliados explicitamente; o agente não deve escolher silenciosamente entre requisitos conflitantes.

## 6. Preparação do ambiente de desenvolvimento

Depois de aprovar o planejamento, peçam ao agente para verificar o sistema operacional, o interpretador Python disponível e as ferramentas necessárias. Cada colega deve ter seu próprio ambiente isolado e instalar as dependências declaradas pelo projeto.

Não há versões fixadas neste kit porque o aplicativo ainda não foi criado. O agente deve propor versões compatíveis, registrar as dependências e fornecer comandos adequados à máquina usada, em vez de pressupor que comandos de Windows, macOS e Linux são iguais.

Ao concluir essa etapa, o novo projeto deve ter seu próprio README de execução, contendo:

1. Pré-requisitos e versões adotadas.
2. Como criar/ativar o ambiente isolado em cada sistema usado pelo grupo.
3. Como instalar as dependências.
4. Como iniciar a aplicação.
5. Como rodar os testes.
6. Como selecionar o modo demonstrativo.
7. Como configurar o Xano futuramente, sem expor segredos.

Este README do kit explica as referências; ele não substitui o README de execução que será criado com o aplicativo.

## 7. Sequência para recriar sem fazer tudo de uma vez

### Etapa A — reconstrução demonstrativa

1. Estrutura do projeto, tema, navegação, login demonstrativo e identificação de perfil.
2. Pacientes: lista, busca, novo cadastro e edição.
3. Profissionais e catálogo de procedimentos.
4. Agenda: lista, filtros, nova consulta, conflito básico e mudança de status.
5. Prontuários: filtro por paciente, histórico e nova evolução.
6. Painel: indicadores derivados dos mesmos dados fictícios usados nas outras áreas.
7. Testes dos três perfis e comparação com os 15 prints.

O painel pode aparecer visualmente desde o início, mas seus números não devem ficar permanentemente fixados. Os fluxos devem compartilhar uma camada coerente de dados simulados: paciente cadastrado deve aparecer nas opções de consulta e prontuário.

Documentar se os dados simulados se perdem ao encerrar/reiniciar a sessão. Persistência simulada entre reinícios, se desejada, deve ser uma escolha explícita do grupo, não uma falsa integração ao Xano.

### Etapa B — integração autorizada

1. Inspecionar ou definir o schema/contrato real do Xano com o grupo.
2. Implementar autenticação e autorização por operação.
3. Substituir os serviços simulados por chamadas reais, por módulo.
4. Validar integridade, conflitos e falhas de rede no backend.
5. Testar persistência e uso em sessões distintas.

Não recriar automaticamente tabelas que já possam existir. Este kit não confirma o estado atual de nenhum workspace Xano. Se o grupo optar por um backend novo, o modelo deverá ser aprovado antes da criação.

### Mensagem para autorizar uma parte

```text
Aprovamos implementar somente [nome da etapa] em modo [demonstrativo ou
integrado], conforme a especificação e a change revisada. Use os prints
[nomes dos arquivos]. Não altere outros módulos ou serviços externos.
Ao terminar, informe arquivos alterados, como executar/testar, resultados
dos testes, diferenças visuais e pendências. Não inicie a etapa seguinte.
```

Substituam os trechos entre colchetes antes de enviar.

## 8. Como usar OpenSpec neste trabalho

O pacote é material de referência, não uma instalação nem um conjunto de changes prontas do OpenSpec.

Peçam ao agente para verificar a ferramenta e sua versão no ambiente, propor a configuração inicial e organizar cada mudança aprovada em requisitos, decisões e tarefas. Usem os comandos suportados pela versão instalada, não nomes de comandos presumidos a partir deste texto.

Para cada parte, o grupo revisa o comportamento esperado antes de aplicar código. Depois, confere evidências de teste e atualiza as especificações. Regras ainda pendentes não devem virar decisões definitivas apenas porque o agente fez uma suposição.

## 9. Como trabalhar em grupo

Uma cópia do mesmo ZIP em vários computadores **não sincroniza o código**. Escolham um repositório compartilhado para o novo aplicativo e uma pessoa responsável por integrar mudanças. Este pacote não cria esse repositório nem configura acesso.

Boas práticas para a divisão:

- Combinem a estrutura, nomes e interfaces dos serviços antes de dividir módulos.
- Cada integrante trabalha na tarefa/branch acordada e apresenta as alterações para revisão.
- Evitem dois agentes alterando simultaneamente o mesmo arquivo, especialmente na mesma pasta compartilhada.
- Não compartilhem senhas pessoais. Acesso ao repositório e ao Xano deve ser individual e autorizado.
- Não incluam ambientes virtuais, caches, arquivos de segredo ou tokens nos commits.
- Guardem este pacote em `referencias/`; requisitos aprovados e atualizados ficam na documentação do novo projeto.
- Antes de iniciar uma tarefa, atualizem a cópia de trabalho pelo fluxo combinado e confirmem quais arquivos estão sob responsabilidade de outra pessoa.

Uma divisão possível é: base visual/autenticação; cadastros; agenda; prontuários/painel; revisão/testes. Ajustem ao tamanho do grupo. A integração final é trabalho conjunto, não apenas juntar telas independentes.

## 10. Revisão do material anterior: o que foi corrigido ou esclarecido

### Independência do ambiente anterior

- O endereço do site permanece em branco e opcional.
- Não há dependência do chat, de login do autor ou de caminhos absolutos de seu computador.
- As fontes antigas de código/documentação são mencionadas apenas como origem da revisão, não como arquivos obrigatórios a fornecer.
- Os 15 prints agora acompanham a especificação no mesmo pacote.

### Escopo de reconstrução

- Separadas explicitamente recriação demonstrativa e integração real. A versão anterior misturava descrições do protótipo com critérios de backend, o que poderia levar o agente a tentar implementar tudo imediatamente.
- Reforçado que o objetivo é recriar as funções e a aparência, não reproduzir defeitos nem ampliar o sistema.
- Mantida a direção técnica registrada, com confirmação inicial e aviso de que Streamlit não garante equivalência pixel a pixel com React.

### Ressalvas dos prints preservados

- Nos prints 03, 04, 05, 07 e 13, o destaque lateral diverge ou pode divergir do conteúdo. O novo aplicativo deve destacar apenas a tela atual. As imagens foram preservadas como capturas históricas, não retocadas.
- O print 06 mostra só a parte visível do histórico. A página deve continuar rolável.
- Não há prints específicos de celular, erro ou estado vazio. Esses estados devem seguir as regras textuais.
- Datas, totais, contatos e textos de teste são exemplos; não copiá-los como regras fixas ou importar como dados reais.

### Limitações funcionais documentadas

- Login e perfis do protótipo são simulação, não autenticação segura.
- Dados antigos ficam no navegador, não no Xano.
- Data de referência e setas da agenda usam valores fixos no protótipo.
- Conflito de agenda antigo verifica horário exato, não sobreposição pela duração.
- “Pacientes ativos” conta cadastros; os rótulos e cálculos do painel precisam ser coerentes.
- Impressão é apenas mensagem; notificações e botão de perfil não abrem funções completas.
- Não há edição/exclusão de profissional, gestão do catálogo, anexos ou impressão real implementados só porque a interface sugere possibilidades.
- Prontuários exigem decisões de autorização e autoria na integração.

Essas observações estão detalhadas por tela na especificação. Elas não significam que todas as melhorias estejam autorizadas para implementação imediata. O grupo deve aprovar as correções em cada etapa.

## 11. Como conferir a fidelidade do resultado

Para cada tela, comparem com seu print e respondam:

- O título, a hierarquia, as informações e a ação principal correspondem à referência?
- Os campos e botões estão presentes e funcionam como descrito?
- O perfil correto vê a ação e o perfil não autorizado não a recebe?
- A navegação leva ao destino esperado, conservando o contexto quando necessário?
- Salvar, cancelar, buscar e filtrar produzem os resultados esperados?
- Há mensagem clara para erro e ausência de resultados?
- O agente explicou qualquer diferença visual relevante do Streamlit?

Na Etapa A, avaliem interface e fluxos simulados. Na Etapa B, acrescentem persistência no Xano, autorização no servidor e testes entre sessões. Não aprovem a integração apenas por ver uma mensagem de sucesso.

O roteiro de 16 testes da especificação serve como checklist de evolução do projeto; os testes de API só passam a ser exigíveis quando a etapa integrada estiver em desenvolvimento.

## 12. Dúvidas comuns

**Preciso acessar o chat original?** Não.

**Preciso preencher o link do site?** Não; é opcional.

**O sistema antigo está dentro do ZIP?** Não. Estão as referências para recriá-lo do zero.

**Preciso ter Xano funcionando para começar?** Não para recriar telas e fluxos demonstrativos. Sim para concluir a etapa integrada.

**O agente precisa de todas as imagens em cada pedido?** Não; deve conhecer o inventário e abrir as relevantes à tarefa. Se não puder ler imagens, informar a limitação e pedir os anexos necessários.

**Posso executar o arquivo Markdown?** Não; ele é documentação, não código.

**O kit prova que atendemos todos os critérios do professor?** Não. O enunciado não está incluído e precisa ser conferido pelo grupo.

**Qual é o primeiro passo agora?** Extrair, organizar conforme a seção 3 e enviar a mensagem inicial da seção 4 ao agente. Revisar o plano antes de autorizar a primeira implementação.
