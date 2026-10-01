# Sorriso+ — Especificação funcional e visual para reconstrução no VS Code

## 1. Instrução inicial para o agente

Estamos desenvolvendo um projeto acadêmico de gerenciamento de clínica odontológica chamado **Sorriso+**. Vamos começar do zero no VS Code e recriar as telas e os fluxos de um protótipo anterior, usando este documento e os 15 prints do pacote. Não presumir acesso ao projeto antigo, ao seu código, ao chat, ao site, a contas ou a um backend pronto.

Leia este documento inteiro antes de implementar. Ele descreve as telas, os formulários, as permissões, as regras e os limites do protótipo. Não interprete exemplos ou limitações como requisitos obrigatórios da aplicação final.

O frontend final definido na documentação do projeto é **Python com Streamlit**, e o backend oficial será **Xano**, acessado por APIs REST. O protótipo existente usa React/TypeScript com Vinext, mas não é necessário reproduzir sua stack nem converter seu código linha a linha. Preserve a organização e os fluxos; adapte os componentes à tecnologia final.

O desenvolvimento deve ser incremental, com documentação e especificações em português brasileiro e uso de **OpenSpec** conforme a configuração disponível no novo projeto. Antes de executar comandos do OpenSpec, verifique a instalação e a versão; não invente comandos ou considere que este documento já constitui uma change aprovada.

Não implemente tudo de uma vez. Primeiro apresente entendimento, dúvidas relevantes, arquitetura proposta e divisão em etapas. O grupo deve poder distribuir as partes e aprovar as mudanças antes de sua implementação. Não crie, altere ou apague tabelas/endpoints no Xano sem uma etapa explicitamente autorizada.

Use exclusivamente dados fictícios. Não solicite senhas pessoais nem chaves administrativas em mensagens. Não publique o projeto automaticamente.

### Referências

- Site do protótipo (opcional): ____________________
- Guia de uso: `README.md`, na raiz do pacote.
- Especificação: este arquivo, dentro de `docs/`.
- Imagens: `referencias-telas/`, na raiz do pacote, com 15 arquivos PNG.

O acesso ao site ou ao chat em que o protótipo foi criado não é necessário. Todos os caminhos acima são relativos à raiz do pacote extraído, e não à máquina de quem criou o protótipo. Os arquivos antigos `app/page.tsx`, `app/globals.css` e `docs/project-overview.md` foram fontes da revisão, mas não fazem parte deste pacote e não são necessários para começar. Se o endereço estiver em branco, prossiga sem solicitar acesso à conta pessoal de qualquer integrante.

Este documento foi elaborado a partir do código local do protótipo. As justificativas abaixo explicam o critério funcional e visual da solução; não são uma transcrição da avaliação ou dos requisitos do professor. A aderência acadêmica deve ser conferida com o enunciado original.

### Como interpretar os requisitos ao começar do zero

**Etapa A — recriação demonstrativa:** reconstruir a aparência, navegação, campos, perfis e fluxos descritos com dados fictícios, na stack acordada. O login pode ser simulado e o repositório de dados pode ser local à sessão, desde que isso seja identificado. Ainda não há garantia de segurança, persistência compartilhada ou integração. Não é necessário conectar ao Xano para validar as telas.

**Etapa B — integração:** substituir a camada simulada pelo Xano, com autenticação, autorização, persistência e regras aprovadas. Esta etapa depende de contratos reais e de autorização do grupo. Não bloquear a Etapa A por falta de credenciais da Etapa B.

As seções “Funcionamento atual” descrevem o protótipo. As seções “Alvo”, “Limitações” e critérios envolvendo API/backend são requisitos ou propostas da etapa integrada, não evidência de que já estejam implementados. Reproduzir as funções, não os defeitos conhecidos. Registrar correções propostas e obter aprovação na change correspondente; não acrescentar novos módulos para corrigir um detalhe.

A decisão de Python/Streamlit + Xano vem da documentação anterior do grupo. Confirmá-la no alinhamento inicial. Se o grupo exigir cópia visual pixel a pixel ou decidir outra stack, apresentar a incompatibilidade/trade-off antes de alterar a tecnologia; não trocar para React silenciosamente.

## 2. Problema e critério de seleção do MVP

O sistema organiza a rotina básica de uma clínica: identificar o paciente, manter os profissionais, marcar a consulta, acompanhar o atendimento e registrar o histórico clínico.

A seleção de telas segue esse fluxo de trabalho, em vez de tentar representar todos os setores de uma clínica. Cada tela tem uma responsabilidade principal:

| Área | Pergunta que responde |
|---|---|
| Login | Quem está acessando e quais funções pode usar? |
| Visão geral | Como está a operação da clínica hoje? |
| Agenda | Quem será atendido, quando e por quem? |
| Pacientes | Quem é o paciente e como localizá-lo? |
| Profissionais | Quem atende e está disponível para novos agendamentos? |
| Prontuários | O que foi realizado e registrado nos atendimentos? |
| Procedimentos | Quais serviços a clínica oferece e seus valores de referência? |

Critérios gerais:

1. Priorizar o fluxo administrativo e clínico essencial.
2. Separar cadastro, agendamento e histórico para evitar duplicação de responsabilidades.
3. Mostrar primeiro as informações necessárias para a ação daquela tela.
4. Usar a mesma linguagem visual e os mesmos padrões de formulário em todo o sistema.
5. Adaptar ações ao papel do usuário.
6. Manter dados relacionados por identificadores, não apenas por nomes digitados.
7. Evitar funções que ampliem desnecessariamente o trabalho acadêmico.

Ficam fora do escopo inicial: pagamentos, faturamento, convênios, estoque, emissão fiscal, WhatsApp/SMS automático, múltiplas unidades, odontograma completo, upload de exames e relatórios avançados. Só devem ser adicionados por decisão posterior do grupo.

## 3. Inventário das telas e das imagens

Existem **sete telas principais, contando o login**, e formulários que aparecem sobre elas. Os 15 prints não representam 15 módulos independentes.

| Print | Conteúdo | Natureza |
|---|---|---|
| 01-login.png | Entrada e escolha de perfil demonstrativo | Tela |
| 02-visao-geral.png | Painel administrativo | Tela |
| 03-agenda.png | Agenda de consultas | Tela |
| 04-pacientes.png | Lista de pacientes | Tela |
| 05-profissionais.png | Equipe da clínica | Tela |
| 06-prontuarios.png | Histórico clínico geral | Tela |
| 07-procedimentos.png | Catálogo de serviços | Tela |
| 08-nova-consulta.png | Agendamento | Formulário/modal |
| 09-novo-paciente.png | Cadastro de paciente | Formulário/modal |
| 10-novo-profissional.png | Cadastro de profissional | Formulário/modal |
| 11-nova-evolucao.png | Registro clínico | Formulário/modal |
| 12-editar-paciente.png | Alteração cadastral | Variação do formulário de paciente |
| 13-prontuario-individual.png | Histórico filtrado de um paciente | Estado da tela Prontuários |
| 14-painel-recepcao.png | Visão geral da recepcionista | Variação por perfil |
| 15-painel-dentista.png | Visão geral da dentista | Variação por perfil |

Os números e nomes de pacientes exibidos nos prints são exemplos. Não fixe os totais das imagens no código.

### Ressalvas verificadas nas imagens

Os prints são capturas da área visível em computador, não documentação de todos os estados nem capturas integrais de páginas longas. O print 06 corta a continuação do histórico abaixo da área visível: manter rolagem e todos os registros. Não há prints específicos de celular, erros ou listas vazias; esses estados estão descritos neste documento.

Nos prints 03, 04, 05, 07 e 13, o destaque do menu lateral pode não coincidir com o título/conteúdo da tela. Não copiar essa inconsistência: selecionar somente a área atual (Agenda, Pacientes, Profissionais, Procedimentos e Prontuários, respectivamente). O título e o conteúdo identificam a tela de referência.

Nos formulários, o fundo desfocado é intencional. Textos de teste, números de registro, datas e contatos das imagens não precisam ser transcritos como base de dados; preparar exemplos fictícios coerentes. A senha `123456` é apenas um recurso da demonstração, nunca uma credencial recomendada para contas reais.

## 4. Perfis e permissões observadas no protótipo

| Operação | Administrador | Recepcionista | Dentista |
|---|---|---|---|
| Ver painel | Sim | Sim | Sim |
| Ver/buscar agenda | Sim | Sim | Sim |
| Criar consulta | Sim | Sim | Não |
| Alterar status da consulta | Sim | Sim | Sim |
| Listar/buscar pacientes | Sim | Sim | Sim |
| Cadastrar/editar paciente | Sim | Sim | Não |
| Consultar profissionais | Sim | Sim | Não |
| Cadastrar/ativar/desativar profissional | Sim | Não | Não |
| Consultar prontuários | Sim | Não | Sim |
| Registrar evolução | Sim | Não | Sim |
| Consultar catálogo de procedimentos | Sim | Não | Não |

Esta é a matriz observada na interface atual, não uma autorização segura implementada no servidor. O protótipo guarda todos os dados no navegador e oculta ações por perfil.

Na aplicação integrada, o Xano deve verificar o usuário e a permissão de cada operação. Esconder um botão não impede acesso indevido à API.

Pontos a decidir com o grupo:

- Dentista verá todos os pacientes/consultas ou apenas os relacionados a ele? No protótipo, não existe filtro automático por profissional autenticado.
- Quais mudanças de status serão permitidas a cada papel? Atualmente todos os três podem escolher qualquer status.
- Recepção pode acessar observações de saúde? Atualmente elas aparecem no formulário de edição do paciente, embora a recepção não veja Prontuários. Na versão integrada, separar dados administrativos e clínicos conforme a política aprovada.
- O cadastro de profissional não cria automaticamente uma conta de usuário. O vínculo entre usuário e profissional precisa ser definido.

## 5. Estrutura comum da interface

### O que aparece

- Marca Sorriso+ no menu lateral.
- Navegação com destaque da área selecionada.
- Contador de consultas do dia ao lado de Agenda.
- Identificação do usuário e de seu perfil.
- Ação Sair.
- Barra superior com `Sorriso+ / Nome da tela`.
- Título, descrição curta e ação principal em cada área.
- Mensagens temporárias de confirmação ou erro.
- Menu recolhível em telas pequenas.

### Critério

O menu permanece consistente para o usuário não precisar reaprender a navegação. O título informa a localização; a ação principal fica próxima dele. Ações secundárias ficam nos itens ou formulários aos quais pertencem.

### Cuidados na reconstrução

- O ícone Notificações e o botão de perfil do cabeçalho são apenas visuais no protótipo: não abrem uma central de notificações nem configurações.
- “Restaurar demonstração” repõe os dados locais iniciais. Não reproduzir essa ação como limpeza do banco compartilhado. Se houver modo de testes, o reset deve ser isolado e explícito.
- Fechar ou cancelar formulário não deve salvar alterações.
- A aplicação final precisa distinguir carregamento, ausência de dados, sucesso, erro e acesso negado.
- Não simular sucesso quando uma chamada ao Xano falhar.

## 6. Tela 1 — Login

**Referência:** 01-login.png.

### Finalidade

Dar entrada no sistema e estabelecer o contexto do usuário antes de mostrar dados e ações.

### Organização visual

No computador, a tela tem duas áreas: apresentação da marca à esquerda, com fundo verde e mensagem sobre organização da clínica; formulário à direita, em fundo claro. No celular, a apresentação lateral é ocultada para priorizar o formulário.

### Funcionamento atual

- Três cartões permitem escolher Administradora, Recepcionista ou Cirurgiã-dentista.
- O e-mail é preenchido automaticamente e não pode ser editado.
- A senha demonstrativa é `123456` para todos os perfis.
- Senha diferente mostra uma mensagem e impede a entrada.
- Ao entrar, abre Visão geral com o nome e as ações do perfil selecionado.
- A sessão demonstrativa é armazenada no navegador.
- Sair remove a sessão, mas não apaga os dados cadastrados.

### Critério

O seletor de perfis facilita apresentar ao professor as diferenças entre usuários sem cadastrar contas durante a demonstração. A apresentação lateral contextualiza o produto.

### Alvo da versão integrada

Login verdadeiro com e-mail e senha, autenticação no Xano e perfil retornado pelo backend. Não permitir que o usuário escolha ser administrador no formulário. Se houver seletor demonstrativo, mantê-lo em modo de demonstração separado, com dados fictícios.

### Critérios de aceite

- Credenciais válidas abrem o painel do usuário correto.
- Credenciais inválidas mostram mensagem compreensível.
- Falha de conexão não é apresentada como senha incorreta.
- Sair encerra a sessão do aplicativo e bloqueia telas protegidas.
- Senhas não são registradas em logs nem armazenadas em texto puro pela aplicação.

## 7. Tela 2 — Visão geral

**Referências:** 02-visao-geral.png, 14-painel-recepcao.png e 15-painel-dentista.png.

### Finalidade

Resumir a operação diária e oferecer atalhos para as tarefas frequentes.

### Componentes e cálculos atuais

1. Saudação pelo primeiro nome do usuário.
2. Data de referência da demonstração.
3. Botão Nova consulta para administração e recepção.
4. Cartão Consultas hoje: total de consultas na data de referência, incluindo canceladas e faltas.
5. Subtexto “ainda aguardando”: quantidade com status Agendada.
6. Cartão Atendimentos: quantidade com status Concluída na data.
7. Cartão Pacientes ativos: na implementação atual, é o total de cadastros; não existe status ativo no paciente.
8. Cartão Próxima consulta: primeiro horário do dia cujo status não seja Concluída, Cancelada ou Falta.
9. Agenda de hoje: até cinco consultas, ordenadas por horário, com paciente, procedimento, profissional e status.
10. Atalho para agenda completa.
11. Acesso rápido: Novo paciente para administração/recepção; Abrir prontuário para administração/dentista; Visualizar agenda para todos.
12. Resumo da quantidade de consultas Confirmadas e uma barra visual de progresso.

### Critério

Indicadores respondem rapidamente “quanto temos hoje?”; a lista mostra “o que vem na rotina?”; os atalhos permitem agir sem percorrer menus. O mesmo painel é reutilizado, com ações adaptadas ao perfil.

### Limitações a corrigir ou especificar

- A data atual é fixa em 24/08/2026. Usar a data real no fuso da clínica na versão integrada.
- “Próxima consulta” não compara o horário com o relógio atual. Definir se será próxima futura ou primeiro atendimento pendente; usar rótulo coerente.
- Renomear “Pacientes ativos” para “Pacientes cadastrados”, salvo se o grupo adicionar um estado de atividade real.
- “Confirmadas para o restante do dia” conta todas as confirmadas da data, não apenas horários futuros.
- A barra atual tem largura mínima de 20%, mesmo sem atendimento concluído. Não reproduzir esse cálculo como indicador fiel; calcular a proporção real, tratar zero consultas e explicitar o denominador.

### Critérios de aceite

- Indicadores são calculados a partir dos dados, não escritos manualmente.
- Mudanças confirmadas na agenda são refletidas no painel.
- Dia vazio não gera divisão por zero nem erro.
- Os três perfis veem somente os atalhos autorizados.

## 8. Tela 3 — Agenda

**Referência:** 03-agenda.png.

### Finalidade

Organizar as consultas por data e acompanhar a situação de cada atendimento.

### Informações exibidas

- Busca por nome do paciente ou procedimento.
- Campo de data.
- Filtro de status, incluindo Todos.
- Data selecionada e quantidade de resultados.
- Lista ordenada por horário.
- Colunas: horário, paciente e telefone, procedimento, profissional e status.
- Botão Nova consulta, disponível à administração e recepção.

### Status existentes

| Status | Significado pretendido |
|---|---|
| Agendada | Consulta registrada, ainda não confirmada |
| Confirmada | Comparecimento confirmado |
| Em atendimento | Atendimento iniciado |
| Concluída | Atendimento finalizado |
| Cancelada | Consulta cancelada |
| Falta | Paciente não compareceu |

Atualmente um seletor altera diretamente o status e apresenta confirmação. Não há regras de transição, justificativa, edição de horário ou exclusão de consulta. Cancelar é uma mudança de status, não a remoção do registro.

### Critério

A lista diária é mais simples para um MVP do que um calendário complexo. Busca, data e status reduzem o esforço para localizar um atendimento. Exibir paciente e profissional evita ambiguidades.

### Limitações e alvo

- As setas do protótipo apontam para datas fixas, 23/08 e 25/08/2026. Na reconstrução, devem subtrair/adicionar um dia à data selecionada.
- Não existe filtro por profissional; só adicionar se aprovado.
- Definir transições de status e autorização no backend.
- Concluir consulta não cria uma evolução clínica automaticamente no protótipo.
- Manter mensagem “Nenhuma consulta encontrada” para filtros sem resultados.

### Critérios de aceite

- Busca, data e status funcionam em conjunto.
- Horários aparecem em ordem crescente.
- Setas navegam relativamente à data atual do filtro.
- Alteração de status só é confirmada após sucesso na API.
- Cancelamento mantém o registro disponível para consulta histórica.

## 9. Formulário — Nova consulta

**Referência:** 08-nova-consulta.png.

| Campo | Tipo/interface | Obrigatório no protótipo |
|---|---|---|
| Paciente | Seleção de paciente cadastrado | Sim |
| Data | Data | Sim |
| Horário | Hora | Sim |
| Profissional | Seleção de profissional ativo | Sim |
| Procedimento | Seleção do catálogo | Sim |
| Observações | Texto multilinha | Não |

### Comportamento

- Abre pelo painel ou pela agenda.
- Usa a data selecionada na agenda como padrão.
- O campo de hora aceita de 08:00 a 18:00 no protótipo.
- Consulta nova recebe status Agendada.
- O protótipo bloqueia outra consulta para o mesmo profissional, na mesma data e no mesmo horário exato, exceto se a existente estiver Cancelada.
- Ao salvar, fecha o formulário, inclui a consulta e ajusta a data selecionada. Quando aberto pelo painel, não navega automaticamente para Agenda.

### Critério

Seletores reutilizam cadastros e reduzem erros de digitação. A checagem de conflito evita o caso mais evidente de agendamento duplicado.

### Regras que precisam ser definidas

- O conflito atual não considera duração: uma consulta às 09:00 com 60 minutos não bloqueia automaticamente outra às 09:30.
- Validar sobreposição por intervalo no backend se esse comportamento fizer parte da change aprovada. A checagem deve também evitar que duas solicitações simultâneas ocupem o mesmo horário.
- Confirmar horário de funcionamento, tratamento de consultas passadas e conflito do próprio paciente.
- Impedir criação se não houver paciente/profissional elegível; explicar o motivo.
- Não criar automaticamente cadastros a partir de texto livre nesse formulário.

### Critérios de aceite

- Campos obrigatórios são validados também no backend.
- Profissional inativo não pode receber nova consulta.
- Conflito mostra mensagem e preserva o preenchimento.
- Salvar uma vez cria apenas uma consulta.

## 10. Tela 4 — Pacientes

**Referência:** 04-pacientes.png.

### Finalidade e conteúdo

Centralizar identificação e contato, permitindo localizar um paciente e abrir seu histórico quando autorizado.

Exibe busca por nome, CPF ou telefone; contador de resultados; botão Novo paciente; e lista com nome, iniciais, nascimento, telefone, e-mail, CPF, última consulta e ações.

### Ações por item

- Editar paciente: administração e recepção.
- Ver prontuário: administração e dentista; abre Prontuários já filtrado para aquele paciente.
- Não existe exclusão de paciente na interface atual.

### Critério

Cadastros administrativos ficam separados das evoluções clínicas. A ação de abrir prontuário conserva o contexto do paciente escolhido, evitando nova busca.

### Limitações

- A busca atual é por trecho de texto, sem tratamento especial de acentos ou normalização de CPF/telefone.
- Não há prevenção de CPF duplicado nem validação de dígitos verificadores.
- A coluna Última consulta é atualizada ao salvar uma evolução, não ao concluir um agendamento.
- Um registro clínico antigo pode substituir essa data por uma mais antiga. Na reconstrução, derivar a data mais recente conforme a definição aprovada.
- Não existe tela separada de ficha detalhada do paciente: há lista, edição e prontuário filtrado.

### Critérios de aceite

- Busca retorna apenas os resultados correspondentes.
- Novo paciente aparece na lista após persistência bem-sucedida.
- Edição mantém o identificador e os vínculos existentes.
- Sem resultados, mostrar mensagem clara e não uma tabela aparentemente quebrada.
- A recepção não obtém acesso a evoluções pela API.

## 11. Formulário — Novo paciente / Editar paciente

**Referências:** 09-novo-paciente.png e 12-editar-paciente.png.

| Campo | Tipo | Obrigatório no protótipo |
|---|---|---|
| Nome completo | Texto | Sim |
| CPF | Texto | Sim |
| Data de nascimento | Data | Sim |
| Telefone | Texto | Sim |
| E-mail | E-mail | Sim |
| Observações de saúde | Texto multilinha | Não |

No cadastro, os campos começam vazios. Na edição, devem vir preenchidos com os dados existentes. O título e a ação principal mudam entre Cadastrar paciente e Salvar alterações. Cancelar ou fechar não altera o cadastro.

**Critério:** um único formulário reutilizável reduz diferenças entre criação e edição. Observações são opcionais para não exigir conteúdo fictício sem necessidade.

**Atenção:** as obrigatoriedades acima descrevem o protótipo; o grupo pode revisar, por exemplo, a exigência de e-mail. Confirmar validação/unicidade de CPF, nascimento válido e tamanho dos campos. A política de dados clínicos da recepção precisa ser resolvida antes de manter Observações de saúde nesse formulário.

**Aceite:** edição não cria novo paciente; erros mantêm o preenchimento; cancelar descarta apenas a edição em andamento; regras aprovadas são verificadas pelo Xano.

## 12. Tela 5 — Profissionais

**Referência:** 05-profissionais.png.

### Finalidade e conteúdo

Consultar a equipe e controlar quais profissionais podem receber novos agendamentos.

Cada cartão mostra iniciais, nome, especialidade, CRO, telefone, e-mail, status Ativo/Inativo e número de consultas na data de referência. Administrador vê Novo profissional e Ativar/Desativar. Recepção apenas consulta. Dentista não tem essa área no menu atual.

### Critério

Cartões agrupam as informações de cada profissional. Inativar em vez de excluir preserva vínculos com consultas e registros antigos.

### Comportamento e limites

- Novo profissional começa Ativo.
- Inativar retira o profissional das opções de Nova consulta.
- Não cancela consultas existentes nem remove prontuários.
- Não existe formulário de edição ou exclusão de profissional.
- O contador inclui todas as consultas da data, sem excluir canceladas.
- Não existe gestão de turnos, férias, bloqueios ou disponibilidade detalhada, apesar de a descrição da tela mencionar disponibilidade.

### Aceite

- Recepção não altera profissionais.
- Inativação mantém o histórico e impede novos agendamentos.
- Reativação devolve o profissional às opções.
- Contadores são derivados dos dados e têm significado documentado.

## 13. Formulário — Novo profissional

**Referência:** 10-novo-profissional.png.

Campos obrigatórios atuais: nome completo, especialidade, CRO, telefone e e-mail. Todos são texto, exceto e-mail com validação de formato do navegador.

**Critério:** registrar o mínimo para identificar o profissional e permitir agendamento. No protótipo, especialidade é texto livre; se o Xano já tiver a tabela Especialidade, o modelo físico deve ser inspecionado antes de trocar por uma seleção vinculada.

Ao salvar, criar profissional Ativo, atualizar a lista e informar sucesso. Não criar conta de acesso automaticamente. Validação/unicidade do CRO e vínculo com usuário serão definidos em mudança específica.

## 14. Tela 6 — Prontuários

**Referências:** 06-prontuarios.png e 13-prontuario-individual.png.

### Finalidade

Consultar o histórico clínico e registrar novas evoluções, mantendo paciente, profissional e data vinculados.

### Componentes

- Filtro de paciente com opção Todos.
- Botão Nova evolução.
- Indicação “Acesso clínico restrito”.
- Lista lateral de pacientes e quantidade de registros.
- Histórico em cartões, ordenado da data mais recente para a mais antiga.
- Cada cartão mostra paciente, data, profissional, procedimento, observações, identificador abreviado e botão Imprimir resumo.

### Funcionamento

Selecionar um paciente no filtro, na lista lateral ou em Ver prontuário na tela Pacientes exibe apenas os registros dele. O prontuário individual é esse estado filtrado; não é outro módulo.

Sem registros, mostrar “Sem evoluções registradas” e orientação para criar a primeira evolução. Não inventar registros para preencher a tela.

### Critério

A ordem cronológica inversa prioriza o atendimento recente. As evoluções ficam separadas em entradas, evitando substituir todo o histórico por um único campo de texto.

### Limitações importantes

- “Pacientes recentes” usa os primeiros cinco pacientes da lista, sem cálculo de recência clínica.
- Imprimir resumo **somente mostra uma mensagem**; não abre impressão nem gera PDF.
- Não há anexos, edição/exclusão de evolução, auditoria nem assinatura digital.
- Não há restrição dos registros por dentista autenticado.
- O aviso de acesso restrito não é uma proteção de backend.

### Aceite

- Recepcionista não visualiza registros nem os recebe da API.
- Filtro nunca mistura registros de outro paciente.
- Histórico mantém os vínculos corretos e a ordenação por data.
- Não exibir um botão de impressão funcional se ele ainda não foi implementado: removê-lo, desabilitá-lo com indicação ou implementar em change própria.
- Política de correção de registros clínicos exige definição explícita; não adicionar exclusão indiscriminada.

## 15. Formulário — Nova evolução clínica

**Referência:** 11-nova-evolucao.png.

| Campo | Interface | Obrigatório |
|---|---|---|
| Paciente | Seleção | Sim |
| Data do atendimento | Data | Sim |
| Profissional | Seleção | Sim |
| Procedimento | Texto livre | Sim |
| Evolução e observações | Texto multilinha | Sim |

### Comportamento atual

- Se o prontuário estiver filtrado, o paciente vem selecionado.
- Data usa a referência fixa da demonstração.
- Para dentista, o profissional padrão é o identificador fixo 1; isso não constitui vínculo real de autenticação.
- O seletor lista também profissionais inativos.
- Ao salvar, cria uma entrada, atualiza Última consulta do paciente para a data informada, fecha e mostra confirmação.
- Não altera automaticamente o status de uma consulta nem exige vínculo com um agendamento.

### Critério

Paciente e profissional identificam a quem pertence o registro e quem atendeu. Texto livre descreve o que foi efetivamente realizado, que pode diferir do serviço previsto na agenda.

### Alvo e aceite

- Associar autoria ao usuário autenticado, sem usar identificador fixo.
- Definir quando o administrador pode registrar em nome de outro profissional; distinguir autor do registro e profissional do atendimento, se necessário.
- Confirmar política para registros retroativos e profissionais inativos.
- Campos obrigatórios devem ser validados no backend.
- Evitar envio duplicado e manter o texto se houver falha de rede.
- Atualização da data mais recente não pode regredir por causa de evolução retroativa.

## 16. Tela 7 — Procedimentos

**Referência:** 07-procedimentos.png.

### Finalidade

Apresentar o catálogo de serviços, duração estimada e preço de referência.

### Conteúdo demonstrativo

| Procedimento | Duração | Valor fictício |
|---|---|---|
| Avaliação | 30 minutos | R$ 120,00 |
| Limpeza e profilaxia | 45 minutos | R$ 180,00 |
| Restauração em resina | 60 minutos | R$ 320,00 |
| Manutenção ortodôntica | 30 minutos | R$ 190,00 |
| Tratamento de canal | 90 minutos | R$ 850,00 |
| Clareamento | 60 minutos | R$ 650,00 |

Somente o administrador acessa a tela. Administração e recepção podem selecionar os serviços no formulário de consulta, mesmo que a recepção não veja o catálogo como área independente.

### Critério

Separar catálogo e consultas permite reutilizar serviços padronizados. Duração e valor contextualizam a operação sem introduzir faturamento.

### Limites e aceite

- O catálogo atual é fixo no código; não existe cadastro, edição ou exclusão pela interface.
- O valor não gera cobrança, conta a receber ou relatório financeiro.
- Duração não controla o conflito no protótipo.
- Na versão integrada, ler serviços do Xano. Gestão do catálogo só será implementada se aprovada.
- Alguns agendamentos antigos demonstrativos têm nomes abreviados ou serviço fora desse catálogo; normalizar os exemplos na nova implementação sem apagar registros existentes por conta própria.
- Formatar moeda em reais e duração com unidade explícita.

## 17. Critérios visuais e adaptação ao Streamlit

### Identidade de referência

| Uso | Cor do protótipo |
|---|---|
| Ação principal e marca | Verde-petróleo `#147c78` |
| Variação escura | `#0f6562` |
| Destaque suave | `#e7f3f1` |
| Fundo | `#f5f8f7` |
| Superfície dos cartões | `#ffffff` |
| Texto principal | `#173038` |
| Texto secundário | `#73848a` |
| Bordas | `#e4ecec` |

A referência utiliza fonte sem serifa (Arial/Helvetica), espaços generosos, bordas finas, cantos arredondados e sombras discretas.

**Critério:** aparência sóbria, leitura rápida e distinção entre ação, conteúdo e contexto. Verde identifica ações; cores suaves de status ajudam a localizar situações, mas devem sempre vir acompanhadas de texto.

### Padrões

- Título de tela, descrição e ação principal com hierarquia consistente.
- Tabelas para comparar muitos registros; cartões para perfis e catálogo; linha do tempo para histórico.
- Formulários curtos em modal no protótipo, mantendo o contexto da tela anterior.
- Rótulos visíveis; não usar apenas placeholder para identificar campo.
- Ícones acompanhados de texto ou descrição acessível.
- Contraste e tamanho de fonte legíveis: não reproduzir rigidamente os textos muito pequenos do protótipo.
- Na versão final, ações críticas devem ter confirmação apropriada.

### Responsividade

O protótipo reorganiza cartões em menos colunas, recolhe o menu no celular e simplifica algumas áreas. As tabelas podem demandar rolagem horizontal.

No Streamlit, preservar a hierarquia e a usabilidade sem exigir reprodução pixel a pixel do CSS React. Preferir componentes suportados e formulários agrupados; não depender de seletores internos frágeis apenas para imitar a imagem. O grupo deve aprovar diferenças visuais relevantes.

## 18. Dados e relacionamentos — modelo conceitual

Este é um modelo de referência, **não uma descrição verificada do schema atual do Xano**. Inspecionar tabelas e campos existentes antes de escrever a integração. Os nomes devem ser mapeados, não presumidos.

| Entidade | Informação principal | Relações |
|---|---|---|
| Usuário | Identidade, e-mail, perfil e estado de acesso | Pode estar vinculado a profissional |
| Paciente | Nome, CPF, nascimento e contatos | Possui consultas e evoluções |
| Especialidade | Nome | Pode ser referenciada por profissionais |
| Profissional | Nome, CRO, contatos e estado de atividade | Possui especialidade e consultas |
| Procedimento | Nome, duração e valor de referência | Referenciado por consultas |
| Consulta | Data/hora, status e observações | Paciente, profissional e procedimento |
| Prontuário/evolução | Data, descrição do atendimento e autoria | Paciente e profissional; eventual consulta |

No protótipo, cada item de prontuário é uma evolução; o histórico do paciente é a coleção desses itens. Não criar automaticamente uma entidade adicional de “cabeçalho de prontuário” sem necessidade do modelo aprovado.

No banco, CPF, telefone e CRO devem ser tratados como identificadores/texto, não números para cálculo. Valores monetários precisam de representação adequada. Datas e horários exigem uma convenção explícita e consistente.

O protótipo guarda paciente/profissional por identificadores, mas procedimento de consulta como texto e especialidade também como texto. Normalizar essas relações é uma mudança da aplicação integrada, não uma funcionalidade já pronta.

## 19. Persistência e integração: o que existe e o que falta

### Situação do protótipo verificado

- Dados em memória e em `localStorage` do navegador.
- Chave de dados: `sorrisomais-demo-data`.
- Chave de sessão: `sorrisomais-user`.
- Identificadores novos gerados com `Date.now()`.
- Catálogo de procedimentos fixo no código.
- Nenhuma integração com Xano no fluxo de negócio de `app/page.tsx`.
- Alterações de um navegador não são automaticamente compartilhadas com outro usuário.

Ter tabelas criadas no Xano não significa que o frontend já esteja conectado.

### Responsabilidades da aplicação final

**Streamlit:** navegação, formulários, feedback, estado temporário de interface e sessão. Não usar estado da sessão como banco definitivo.

**Xano:** dados persistentes, autenticação, autorização por operação, validações, geração de identificadores e regras críticas.

Antes da integração, obter o contrato real da API: ambiente/base URL, autenticação, endpoints disponíveis, métodos, campos, formatos de resposta, filtros/paginação e códigos de erro. Não inventar endpoints e alegar integração concluída.

Se o backend estiver indisponível, usar uma camada de dados simulada explicitamente identificada, com a mesma interface esperada, sem misturá-la silenciosamente aos dados integrados.

Segredos devem ficar fora do repositório. Fornecer apenas arquivo de exemplo de configuração sem valores secretos. Tratar tokens como credenciais, isolar sessões de usuários e não usar cache compartilhado para dados privados sem separação apropriada.

## 20. Organização sugerida para o novo projeto

Não é necessário colocar tudo em um único arquivo. Separar conceitualmente:

- entrada e configuração da aplicação;
- telas de login, painel, agenda, pacientes, profissionais, prontuários e procedimentos;
- componentes reutilizáveis e formulários;
- cliente da API Xano;
- serviços de autenticação e acesso aos dados;
- modelos, validações e regras de apresentação;
- testes;
- documentação e artefatos OpenSpec.

A estrutura exata de diretórios deverá ser proposta depois de verificar o projeto novo e a versão de Streamlit. Não reutilizar dependências da hospedagem React apenas porque aparecem no protótipo.

## 21. Etapas sugeridas para dividir com o grupo

1. **Alinhamento:** confirmar enunciado, stack, escopo, permissões e contrato de dados; configurar documentação/OpenSpec.
2. **Base visual:** tema, navegação e telas com dados simulados identificados, sem mexer no Xano.
3. **Autenticação:** login integrado, sessão, logout e autorização no backend.
4. **Cadastros:** pacientes e profissionais, preservando vínculos.
5. **Catálogo e agenda:** leitura de procedimentos, criação de consulta, filtros, conflitos e status.
6. **Prontuários:** histórico, filtros, evolução e autorização clínica.
7. **Painel:** indicadores derivados das regras já aprovadas.
8. **Validação:** testes, responsividade, documentação e demonstração com dados fictícios.

Para cada etapa: descrever proposta, requisitos e cenários; revisar com o grupo; implementar apenas o aprovado; testar; documentar o resultado e consolidar a especificação. Usar o fluxo disponível do OpenSpec instalado, sem assumir que os nomes de comandos permanecem iguais entre versões.

## 22. Roteiro de demonstração e testes finais

1. Entrar como administrador e conferir as áreas permitidas.
2. Cadastrar um paciente fictício e localizá-lo pela busca.
3. Editá-lo sem criar duplicata.
4. Cadastrar um profissional e confirmar que aparece no agendamento.
5. Criar consulta relacionando paciente, profissional e procedimento.
6. Tentar um conflito coberto pela regra aprovada e verificar rejeição.
7. Filtrar agenda por data, texto e status.
8. Alterar o status e conferir a atualização dos indicadores.
9. Abrir o prontuário pelo paciente e salvar uma evolução fictícia.
10. Confirmar que outro paciente não recebeu esse registro.
11. Entrar como recepção e testar tanto a ausência da tela clínica quanto a rejeição de acesso não autorizado pela API.
12. Entrar como dentista e conferir as permissões aprovadas.
13. Inativar profissional e verificar que histórico permanece, mas novo agendamento é bloqueado.
14. Simular API indisponível e confirmar mensagem de erro sem falso sucesso nem perda desnecessária do preenchimento.
15. Atualizar/reabrir a aplicação e confirmar persistência no Xano; verificar em sessão separada quando autorizado.
16. Conferir telas vazias e apresentação em tela pequena.

Não considerar a etapa concluída apenas porque a interface parece pronta. Registrar o que foi implementado, o que foi testado e o que continua simulado ou pendente.

## 23. Primeira resposta esperada do agente do VS Code

Antes de escrever código, responda com:

1. Seu entendimento do projeto e da stack definida.
2. O que já existe no novo ambiente e o que está faltando.
3. A separação entre comportamentos a preservar e limitações a corrigir.
4. A estrutura proposta de arquivos e responsabilidades.
5. A primeira change/etapa pequena sugerida e seus critérios de aceite.
6. As informações realmente necessárias para começar, sem pedir credenciais pessoais.

Não inicie todas as etapas automaticamente. Aguarde o grupo escolher a primeira parte a implementar.
