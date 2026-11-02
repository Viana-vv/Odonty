# Ícones da interface

## Escopo e procedência

A change `substituir-icones-regen` unifica a iconografia das interfaces Python/Streamlit com SVGs locais Regen, preservando layout, funcionalidades, permissões, imagens, mascotes e marca. Não altera backend, contratos REST ou regras do domínio.

Fonte: [kazdenc/regen-icons](https://github.com/kazdenc/regen-icons), commit `64c0e165c3ce6d5c9d7329acf5762306f86d6b1d`. Foram incorporados 53 SVGs outline; seus nomes e hashes SHA-256 constam de `assets/icones/regen/origem.json`. A licença MIT está em `assets/icones/regen/LICENSE`. Os recursos são locais e não dependem de CDN, pacote npm, gerador ou acesso à rede em execução.

O inventário considera README, AGENTS, os três documentos de contexto em `docs/`, as 34 specs vigentes e os pontos de renderização Python/CSS. As linhas abaixo são referências do levantamento inicial, antes das substituições; nomes de funções e chaves são referências mais estáveis após edições.

## Renderização compartilhada

`sorrisomais/icones.py` concentra:

- `svg_icone(nome)`: leitura local e validação do vetor.
- `icone_html(nome, classe='')`: SVG decorativo para conteúdo HTML.
- `icone_metrica(rotulo)`: SVG dentro de `span.icone-metrica`.
- `estilos_icones()`: máscaras CSS para controles nativos, aplicadas pelas entradas `app.py` e `portal_paciente.py`.

O validador restringe elementos a `svg` e `path`, limita atributos e rejeita declarações, eventos, elementos ativos e referências externas. Os SVGs usados como máscaras são codificados em URI `data:` a partir dos arquivos locais, sem servidor gráfico externo. Nomes dinâmicos apresentados junto ao HTML devem ser escapados; a identificação da equipe escapa nome e iniciais.

| Significado da métrica | Vetor |
|---|---|
| Consultas hoje | `calendar` |
| Atendimentos | `clipboard-check` |
| Pacientes ativos | `users` |
| Próxima consulta | `clock` |
| Confirmadas | `calendar-check` |
| Prontuários | `file-text` |
| Rótulo sem mapeamento específico | `circle-check` |

O conjunto adotado não possui dente. Procedimentos usam `tool`; Atendimentos usam `clipboard-check`. Não se mantém um desenho de outra família para esses conceitos.

## Inventário e cobertura das telas

Os arquivos Python da tabela pertencem a `sorrisomais/`, salvo indicação contrária. A cobertura por CSS descreve os pontos de aplicação; sua presença não comprova sozinha o resultado visual no navegador.

| Tela ou superfície | Arquivos e referências iniciais | Forma anterior e cobertura |
|---|---|---|
| Login da equipe | `app.py:83–85` | E-mail, senha e Entrar eram textuais; máscara no botão nativo e tratamento do controle de visibilidade da senha. Marca e arte preservadas. |
| Login do Paciente | `portal_paciente.py`; `autoatendimento_paciente.py:122` | Entrada própria do portal; controles nativos recebem os estilos compartilhados sem alterar autenticação. |
| Portal autenticado do Paciente | `autoatendimento_paciente.py:138–152` | Sair, abas Consultas/Informações liberadas/Exames e ações de atualização. Botões recebem máscaras; abas mantêm seus textos. |
| Consultas do Paciente | `pagina_consultas_paciente.py:36` | Atualizar Consultas era textual. Listas futuras/passadas e mensagens permanecem funcionais. |
| Menu da equipe | `paginas_equipe.py:1079–1116` | Material `home`, `calendar_month`, `groups`, `badge`, `description`, `dentistry` e fallback `folder_open`; parâmetros removidos em favor das máscaras por chaves existentes. |
| Painel da Recepção | `paginas_equipe.py:98–208` | Saudação com mão, métricas `▣`, `✓`, `◷`, criação `+`, agenda `▦` e seta `→`. Saudação textual, métricas compartilhadas e botões com rótulos sem pictogramas. |
| Painel administrativo | `paginas_equipe.py:819–946` | Mão, `□`, `✓`, `♙`, `◷`, `＋`, `▤`, `▦` e `→`; mesma estratégia de substituição. |
| Painel alternativo/indisponível | `paginas_equipe.py:975–1024` | Métricas `▢`, `✓`, `♙`, `◷` e atalhos com glifos; também coberto, incluindo botões desabilitados. |
| Painel do Profissional | `painel_profissional.py:77–148` | Métricas `▦`, `✓`, `▤`, `◷`, mão e atalhos com setas. Métricas compartilham o helper; rótulos textuais preservam as ações. |
| Identificação da equipe | `paginas_equipe.py:1181` | `◉` substituído por `user`, com nome e iniciais escapados. A topbar permanece oculta pelo CSS existente. |
| Agenda e gestão de Disponibilidades | `paginas_equipe.py:352–647` | Material `tune`, criação `＋`, navegação `‹`/`›`; popover e botões recebem máscaras. Botões isolados passam a Dia anterior/Dia seguinte, preservando chaves e tooltips. Expanders, seletores, datas e números são controles nativos. |
| Nova Consulta | `pagina_nova_consulta_xano.py:82–153` | Atualização, seletores, cancelar e agendar eram textuais; cobertura pelos estilos dos controles nativos. |
| Reagendamento | `pagina_reagendar_consulta_xano.py:48–166` | Seletores, data, atualizar, cancelar e confirmar; mesma cobertura, sem alterar dependência entre escolhas. |
| Listagem e edição de Pacientes | `pagina_pacientes_xano.py:60–79,135–194` | `＋ Novo Paciente`, busca, atualizar, editar e formulário; retirada do glifo e máscaras nos controles existentes. Avatares com iniciais preservados. |
| Cadastro de Paciente | `pagina_paciente.py:86–144` | Submissão/reenvio/cancelar textuais e fechar `×`; Fechar conserva o controle nativo. |
| Listagem e gestão de Profissionais | `pagina_profissionais_xano.py:32–40,72,98` | Atualização, confirmação e alteração de situação; máscaras nos botões existentes. Iniciais e badges preservados. |
| Cadastro de Profissional | `paginas_equipe.py:713–789` | Atualização, senha e submissão; fechar `×` passa a Fechar. Não muda agrupamento dos campos ou permissões. |
| Prontuário e Registros Clínicos | `pagina_prontuario_xano.py:96,147–162` | Atualizar, seletor, acesso restrito `◉` e seta `›` na seleção. Acesso restrito usa `shield-check`; ações mantêm nomes textuais e máscaras. |
| Nova Evolução | `pagina_nova_evolucao_xano.py:48–105` | Abrir, seletores, salvar, cancelar e fechar `×`; fechamento textual e controles nativos, sem mudar rascunhos ou vínculo ao Paciente. |
| Catálogo de Procedimentos | `pagina_procedimentos_xano.py:34–64` | Dente em SVG inline próprio substituído por `tool`; busca/atualizar/repetir usam controles existentes. |
| Procedimentos da Consulta | `pagina_procedimentos_consulta.py:67,141` | Marcar como realizado e Atualizar Procedimentos eram textuais; recebem máscaras sem mudar transições. |
| Exames | `pagina_exames_xano.py:33–58,121–132` | Expanders, situação, datas, solicitar e salvar; cobertura compartilhada dos widgets, preservando conteúdo e autorização. |
| Contas de Acesso | `pagina_contas_acesso_xano.py:37–39,72` | Atualizar lista e cartões com iniciais; controles recebem estilos comuns. O módulo existe, mas não consta de `AREAS`/`MODULOS_XANO` no roteador auditado; não se cria navegação nova para justificar um ícone. |
| Demonstração: início | `paginas_demo.py:38–41,110–133` | Métricas `▣`, `✓`, `♙`, `◷` e atalhos `→`/`›`; helper nas métricas e rótulos sem glifos. |
| Demonstração: Agenda, Pacientes e Profissionais | `paginas_demo.py:151,212,241` | Criação `+` removida dos rótulos; formulários, listagens e alteração de situação continuam no repositório fictício da sessão. |
| Demonstração: Prontuário/Nova Evolução e Procedimentos | `paginas_demo.py:289–328` | Nova evolução perde o prefixo `+`; ações e catálogo preservados. |
| Demonstração: menu e aviso | `paginas_demo.py:362–377` | Chaves `demo-nav-*` possuem mapeamento equivalente ao menu conectado; o aviso usa ícone vetorial de informação no lugar do emoji. |
| Compatibilidade de ilustrações | `ilustracoes.py:51–60` no inventário original | Helper antigo com calendário/pessoas/dente/relógio/check inline passa a reutilizar o helper central, evitando uma segunda família ao reaproveitar essa interface. |

## Imagens e composição preservadas

- Os 16 PNGs em `assets/mascotes-tratados/` e seus originais não fazem parte da substituição de ícones.
- Marca/assinatura, banners contextuais e ilustrações de estados continuam em `ilustracoes.py`.
- Favicons de `app.py` e `portal_paciente.py` continuam baseados no mascote.
- O `+` de Sorriso+ é parte da marca e deve permanecer.
- Iniciais dos avatares, badges de situação, textos, ondas, curvas, fundos e sobreposições de modais não são pictogramas substituíveis.
- Em `assets/estilos.css`, `.icone-metrica` e `.icone-procedimento` mantêm seus contêineres e cores. O inventário não encontrou ícones em `content:` ou SVGs em background/mask nesse arquivo original; seus pseudo-elementos formam decoração e rótulos responsivos.

## Auditoria externa: alcance e limites

A revisão estática do repositório externo examinou os manifests, lockfile, workflow, scripts do gerador e 384 SVGs da revisão fixa. Os vetores contêm apenas `svg` e `path`, sem scripts, eventos ou referências externas. Os manifests não possuem hooks de instalação; os scripts usam operações de arquivos para build local e processos para abrir navegador local ou executar `tsc`. O gerador declara cinco dependências diretas de desenvolvimento e o lockfile resolve sete pacotes ao todo.

Não foram encontrados indícios de conteúdo malicioso no escopo examinado. Não foram instaladas dependências nem executados scripts ou gerador externos. A análise não comprova ausência de vulnerabilidades nas dependências nem ausência absoluta de malware, e não se estende automaticamente a revisões futuras. Somente SVGs e licença foram incorporados. Os testes conferem seus hashes e rejeitam vetores com conteúdo ativo, referências externas e tentativa de escapar da pasta dos ícones.

## Limites de integração e verificação

O projeto fixa Streamlit 1.64.0. Não se passa SVG arbitrário ao parâmetro `icon` nem se transforma botão funcional em HTML estático. SVG inline é usado para conteúdo decorativo; máscaras CSS preservam botões, chaves, callbacks, flags e submissão nativos, herdando a cor por `currentColor`.

A implementação de máscaras depende de `data-testid`, classes por chave e estrutura interna do Streamlit, adaptada ao DOM React Aria conferido no navegador. Atualizações do framework exigem nova conferência. Os mapeamentos exatos prevalecem sobre grupos de ações; botões sem mapeamento específico usam seta de ação. Os nomes e chaves continuam nativos, inclusive Fechar e navegação entre dias, cujos textos ficam disponíveis para leitores de tela.

O helper trata botões, submissões, popover, alertas, expansão, seleção, calendário e sua navegação interna, visibilidade de senha, checkboxes, incremento/decremento, links de cabeçalho e carregamento animado. Abas e campos de busca textuais continuam textuais. O projeto não usa ferramentas interativas de tabela nesta revisão. Elementos do navegador e da infraestrutura do Streamlit fora do conteúdo da aplicação não fazem parte do conjunto de ícones do site.

Na etapa dos três arquivos delegados (`paginas_equipe.py`, `paginas_demo.py`, `painel_profissional.py`), passaram compilação em memória, análise de sintaxe/estrutura das métricas, comparação de chaves/callbacks/flags dos widgets e `git diff --check`. A busca estática não encontrou os glifos substituídos nesses arquivos.

Verificação final: 255 testes Python aprovados, incluindo 11 testes de procedência e segurança dos vetores. As 18 composições do roteiro de referências e 12 composições adicionais de portal, Contas de Acesso, Procedimentos da Consulta, demonstração, controles e carregamento passaram em desktop e celular, totalizando 30 composições em duas resoluções.

Foram verificados nomes acessíveis, máscaras com contraste herdado, estados desabilitados, teclado, fechamento de modais, independência de rolagens, calendário, alteração de seleção, checkbox, quantidade e visibilidade de senha. O roteiro adicional bloqueia requisições externas; os clientes usam exclusivamente dados fictícios. O diff do Git confirma ausência de alterações nas imagens, nos 16 PNGs tratados e no CSS de composição original.

Reprodução: `.venv/Scripts/python -B tests/visual/conferir_referencias.py` e `.venv/Scripts/python -B tests/visual/conferir_icones.py`. Capturas locais em `test-results/reconstrucao-frontend/` e `test-results/icones-regen/`; esses artefatos não integram o commit. Testes visuais simulados não equivalem a uma validação autenticada no Xano.
