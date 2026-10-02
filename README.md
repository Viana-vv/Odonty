# Sorriso+

MVP acadêmico com Python/Streamlit na interface e Xano para autenticação, autorização e dados via API REST. Implantação pública prevista em Render ou Railway.

## Estado atual

Login, identificação da Conta de Acesso, sessão de uma hora e logout estão implementados e validados no Xano. Administrador também pode cadastrar profissionais; Profissional aparece como Dentista. **O cadastro de Paciente está funcionando e pronto para uso demonstrativo** por Administrador e Recepcionista, com autorização aplicada no Xano. Recuperação de senha e funcionalidades clínicas permanecem fora desta entrega.

As telas existentes de login, início da equipe e cadastros de Paciente e Profissional usam a identidade visual Sorriso+ e o mascote local `assets/1000323602.jpg`. A navegação exibe somente ações disponíveis para o perfil autenticado; módulos que ainda não possuem fluxo não aparecem como opções.

Issue: [#1](https://github.com/Viana-vv/Odonty/issues/1). Implementação na branch `feat/1-login-streamlit-xano`, preparada para revisão do grupo.

## Executar localmente

Use Python 3.10 ou superior. Execute os comandos a partir da raiz do repositório. Crie um ambiente virtual local, instale as dependências de desenvolvimento e configure a URL HTTPS do grupo de API do Xano.

### macOS (Terminal, zsh ou bash)

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
export XANO_API_BASE_URL="https://sua-instancia.xano.io/api:seu-grupo"
export XANO_HTTP_TIMEOUT_SECONDS="10"
.venv/bin/python -m streamlit run app.py
```

### Windows (PowerShell)

```powershell
py -3 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
$env:XANO_API_BASE_URL = "https://sua-instancia.xano.io/api:seu-grupo"
$env:XANO_HTTP_TIMEOUT_SECONDS = "10"
.venv\Scripts\python.exe -m streamlit run app.py
```

Abra **http://localhost:8501**. Substitua o endereço ilustrativo pela URL HTTPS do grupo publicado. Para executar sem ferramentas de teste, instale `requirements.txt`.

O grupo validado nesta entrega é `https://x8ki-letl-twmt.n7.xano.io/api:sorriso-acesso:v1`. Cada terminal novo precisa receber `XANO_API_BASE_URL` antes de iniciar o Streamlit. Os comandos acima configuram a variável somente no terminal atual.

O arquivo `.env.example` é uma referência: a aplicação não carrega `.env` automaticamente. Credenciais administrativas do Xano não são credenciais de login e não devem ser usadas no frontend.

| Variável | Ambiente | Configuração |
|---|---|---|
| `XANO_API_BASE_URL` | Streamlit | Obrigatória; HTTPS, sem credenciais, query string ou fragmento |
| `XANO_HTTP_TIMEOUT_SECONDS` | Streamlit | Opcional; número positivo e finito, padrão 10 segundos |
| `XANO_CADASTRO_PACIENTE_HABILITADO` | Streamlit | Opcional; habilitado por padrão após publicação e validação do endpoint; definir `0` para ocultar a ação |
| `SORRISOMAIS_MODO_DEMONSTRACAO` | Streamlit | Opcional; padrão `0`; definir `1` para habilitar telas com dados fictícios limitados à sessão. O login continua usando Xano |
| `AUTH_SESSION_TTL_SECONDS` | Xano | Padrão 3600 segundos; valores menores somente em testes isolados |

Sem configuração válida, a tela informa o problema e desabilita o formulário.

No modo Xano atual, permanecem disponíveis login, identificação e logout,
cadastro de Paciente, cadastro de Profissional e listagem de Especialidades
necessária ao cadastro. Agenda, Consultas, listagens e perfil de Paciente,
Prontuários e Registros Clínicos ainda não têm integração Xano confirmada;
essas áreas aparecem somente na demonstração fictícia até aprovação de uma
change própria baseada no contrato real.

Na branch `feat/3-retomada-cadastro-profissional`, os métodos clientes e os
testes unitários locais dos contratos propostos para Disponibilidades, Consultas
e Registros Clínicos foram iniciados conforme a change
`agenda-consultas-registros-clinicos-api`. Isso não significa que as rotas estejam
publicadas ou validadas no Xano. A criação das tabelas e endpoints, autorização,
transações, concorrência e isolamento clínico ainda dependem de verificação em
um workspace de teste do Xano.

Para respeitar o limite de requisições do workspace, a Conta de Acesso é
revalidada no máximo uma vez a cada 20 segundos durante reruns da interface.
O Xano continua validando cada operação protegida. A lista de Especialidades
fica no estado da sessão por 5 minutos; depois de erro, uma nova tentativa
aguarda 20 segundos. Nenhum desses caches é compartilhado entre sessões.

## Estrutura e contrato

- `app.py` e `assets/`: interface e identidade visual.
- `sorrisomais/config.py`: configuração.
- `sorrisomais/api.py`: chamadas REST e validação de respostas.
- `sorrisomais/sessao.py`: entrada, revalidação e saída.
- `backend/xano/`: Conta de Acesso, Sessão de Acesso, validação e endpoints.

| Rota relativa à URL base | Entrada | Sucesso |
|---|---|---|
| `POST /auth/login` | JSON com `email` e `senha` | 200 com `token`, `tipo_token` e `expira_em` |
| `GET /auth/me` | Bearer token | 200 com `conta` e `expira_em` |
| `POST /auth/logout` | Bearer token | 204 sem corpo |
| `GET /especialidades` | Bearer token de Administrador | 200 com especialidades ativas |
| `POST /profissionais` | Bearer token de Administrador e JSON estrito | 201 com Profissional e Conta de Acesso vinculados |

O cadastro de Profissional exige `nome`, `email`, `senha`, `cro` e `especialidade_id`. A confirmação da senha é validada somente na interface e não é enviada. O backend normaliza e-mail e CRO, exige uma especialidade ativa e define o único perfil da nova Conta de Acesso como `profissional`. A resposta não contém senha, e-mail, hash ou token. A autorização é verificada no Xano em cada chamada.

Erros esperados no cadastro: 400 para dados inválidos, 401 para sessão inválida, 403 para acesso não autorizado, 409 para e-mail ou CRO duplicado e 429 para limite de requisições. Timeout, erro 5xx ou resposta incompatível são tratados como resultado não confirmado; o cliente não repete automaticamente a operação. Consulte a [especificação de cadastro de Profissional](openspec/specs/cadastro-profissional/spec.md) para os requisitos e cenários do fluxo.

Na auditoria local de 02/10/2026, passaram 156 testes Python de contratos, cadastro, autenticação e interface. Os cinco testes JavaScript de login, identidade, logout, especialidades e cadastro de Profissional também passaram. Esses testes substituem a rede por respostas simuladas e não fazem parte de uma validação do Xano publicado; não comprovam permissões, transações ou concorrência no backend.

O [design](openspec/changes/archive/2026-09-25-login-streamlit-xano/design.md) detalha o contrato e as permissões. As tabelas legadas e APIs de outras funcionalidades foram preservadas.

O token fica no estado da sessão Streamlit. A identidade é revalidada antes da exibição protegida. A sessão tem prazo absoluto de uma hora, sem renovação. O logout sempre limpa o estado local e informa quando não confirmou a revogação remota. Nova conexão sem estado exige novo login.

## Testar

Os comandos abaixo usam diretamente o Python do ambiente virtual e funcionam sem ativar o ambiente. No Windows, use `.venv\Scripts\python.exe` no lugar de `.venv/bin/python`.

Para navegar pelas telas demonstrativas, defina `SORRISOMAIS_MODO_DEMONSTRACAO=1`. É necessário autenticar no Xano; os dados demonstrativos não são gravados no backend e desaparecem ao encerrar a sessão.

```sh
.venv/bin/python -m pytest tests/test_acesso.py tests/test_interface.py -q
openspec validate --all --strict
```

Cada rota REST `GET` ou `POST` possui testes unitários separados em Python
(`tests/api_contracts/`) e JavaScript (`tests/js/api_contracts/`). Execute-os
sem rede com:

```sh
.venv/bin/python -B -m pytest tests/api_contracts -q -p no:cacheprovider
node --test tests/js/api_contracts/auth-login.test.mjs tests/js/api_contracts/auth-me.test.mjs tests/js/api_contracts/auth-logout.test.mjs tests/js/api_contracts/pacientes-post.test.mjs tests/js/api_contracts/profissionais-post.test.mjs tests/js/api_contracts/especialidades-get.test.mjs tests/js/api_contracts/client-options.test.mjs
```

Em 23/09/2026, **54 testes locais e 25 testes reais passaram**. Os testes locais verificam configuração, contrato, falhas de rede, erros seguros e comportamento da interface. A suíte real verifica diretamente no Xano campos, perfis, contas bloqueadas/inativas, identidade própria, revogação, replay, logout repetido, perda de acesso, sessões independentes e expiração efetiva.

Para repetir os testes reais, configure `XANO_API_BASE_URL`, `XANO_METADATA_BASE_URL`, `XANO_WORKSPACE_ID` e `XANO_METADATA_TOKEN` no ambiente. O token administrativo deve vir de uma fonte segura e nunca ser salvo no repositório.

Para inspeção de tabelas, schemas e demais chamadas da Metadata API, use `XANO_METADATA_BASE_URL=https://x8ki-letl-twmt.n7.xano.io/api:meta` com `Authorization: Bearer` usando `XANO_METADATA_TOKEN`. Acrescente `/workspace/{XANO_WORKSPACE_ID}` para operações do workspace. Não derive esse endereço de `XANO_API_BASE_URL`, que aponta exclusivamente para o grupo de API do projeto. Skills e ferramentas de inspeção devem seguir essa mesma separação.

```sh
XANO_TESTAR_REAL=1 .venv/bin/python -m pytest tests/test_xano_real.py -q --tb=short
```

No PowerShell:

```powershell
$env:XANO_TESTAR_REAL = "1"
.venv\Scripts\python.exe -m pytest tests/test_xano_real.py -q --tb=short
```

Sem a opção explícita, os testes reais são ignorados. A suíte cria somente contas fictícias, com senhas aleatórias transformadas pelo campo password do Xano, e as inativa ao terminar. O teste de expiração cria um grupo temporário com validade de oito segundos e o remove em `finally`; o grupo principal permanece com uma hora. Nenhuma verificação depende de ignorar o prazo ou alterar o relógio.

As chamadas da suíte são espaçadas para respeitar o limite do plano Xano. HTTP 429 pode prolongar a execução. A aplicação não repete automaticamente login ou logout.

Também foram verificados: computador (1440 px), tablet (768 px), celular (390 px), ausência de rolagem horizontal, foco de teclado, senha mascarada, uma única chamada após clique duplo e bloqueio do formulário durante o envio. O fluxo completo navegador → Streamlit → Xano foi confirmado com entrada, identidade e saída.

Os três endpoints usam `history = false`; o histórico do grupo permaneceu vazio após os testes. Evidências locais sem credenciais ficam em `test-results/`, ignorado pelo Git.

## Acesso administrativo fictício

O login é feito com uma Conta de Acesso ativa cujo perfil foi autorizado no Xano. Para testar como Administrador em outra máquina, solicite ao responsável pelo workspace uma conta administrativa fictícia individual ou o provisionamento de uma conta de teste. O responsável deve entregar os dados de acesso por um canal seguro; não reutilize senha pessoal, não a coloque em `.env`, arquivos do projeto, capturas de tela ou no Git. Digite a senha diretamente no formulário de login.

Arquivos de credenciais locais de outra máquina não são necessários e não devem ser copiados. A autorização continua sendo verificada pelo Xano: a interface apresenta as ações administrativas somente quando a Conta de Acesso autenticada retorna o perfil Administrador. Sem uma conta fictícia ativa e autorizada no Xano, é possível iniciar o app, mas não concluir o login administrativo.

## Documentação

### Cadastro de Paciente — funcionando e pronto

O fluxo está publicado e funcionando no Xano para Administrador e Recepcionista. A integração real foi aprovada em 62 testes no grupo temporário; criação e reenvio idempotente foram confirmados no endpoint publicado. A interface também foi verificada no navegador para os dois perfis em computador, tablet e celular, com navegação por teclado. O cadastro cria um Paciente e seu Prontuário; não cria Conta de Acesso para o Paciente. Use somente dados fictícios.

### Cadastro de pacientes — detalhes da implementação

O endpoint de cadastro foi publicado e validado no Xano em 27/09/2026. **Cadastrar paciente** fica disponível por padrão para Administrador e Recepcionista autenticados. Para ocultar a ação em uma implantação, defina `XANO_CADASTRO_PACIENTE_HABILITADO=0` antes de iniciar o Streamlit. Essa opção controla apenas a interface; a autorização efetiva é aplicada no endpoint.

- **Nome completo \***: obrigatório, de 2 a 120 caracteres após remover espaços externos.
- **Data de nascimento \***: obrigatória, data real até hoje em `America/Sao_Paulo`.
- **Telefone \***: obrigatório, com 10 ou 11 dígitos nacionais após normalizar espaços, parênteses e hífen.
- **CPF \***: obrigatório, com formato e dígitos verificadores válidos; persistido sem máscara.
- **E-mail \*** e **Celular \***: obrigatórios, normalizados e validados. Familiares podem compartilhar contato.

O formulário não solicita senha nem cria login do Paciente. **Cadastrar** envia uma operação; **Voltar** limpa o formulário. Sucesso limpa os campos e preserva a sessão da equipe. Rejeição por dados inválidos ou CPF duplicado preserva os campos e permite correção. Após resultado incerto, **Reenviar mesma operação** utiliza a mesma chave e os mesmos dados; não há repetição automática. Sair ou voltar não desfaz um cadastro possivelmente concluído, e perder a sessão perde a chave local: conferir o resultado antes de abrir outra operação.

Contrato publicado: `POST /pacientes`, Bearer token, JSON com `nome`, `data_nascimento` em `YYYY-MM-DD`, `telefone`, `cpf`, `email`, `celular` (todos obrigatórios) e `operacao_id` UUID v4. Resposta 201: `{"paciente":{"id":123,"nome":"Paciente Fictício","situacao":"ativo"},"operacao_id":"mesmo-UUID-enviado"}`. Erros esperados: 400, 401, 403, 409 com `CPF_DUPLICADO` ou `OPERACAO_CONFLITANTE`, 429 e indisponibilidade. Mensagens recebidas do servidor não são exibidas diretamente.

**Verificado no Xano em 27/09/2026:** índice único de CPF e campos `situacao` e `atualizado_em` na tabela Paciente, após auditoria que encontrou a tabela vazia. A validação de CPF e nascimento do endpoint versionado passou em 26 testes reais, usando grupo temporário autenticado sem gravar Pacientes. O schema está em `backend/xano/table/paciente.xs`.

**Cadastro de Paciente:** endpoint `POST /pacientes` publicado no grupo principal do Xano em 27/09/2026. A integração real completa passou em 62 testes no grupo temporário; o smoke test do endpoint publicado confirmou criação e replay idempotente. O fluxo visual foi verificado no Chrome para Administrador e Recepcionista em computador, tablet e celular, incluindo teclado e ausência de rolagem horizontal. Contas e Pacientes de teste foram inativados, e o grupo temporário removido. Capturas fictícias estão em `test-results/cadastro-paciente/` (ignorado pelo Git).

Para repetir apenas a verificação real de CPF, nascimento e schema, configure as mesmas quatro variáveis administrativas descritas na seção de testes e execute:

```powershell
$env:XANO_TESTAR_PACIENTE = "1"
.venv\Scripts\python.exe -B -m pytest tests/test_xano_pacientes_real.py -q --tb=short
```

No macOS, execute `XANO_TESTAR_PACIENTE=1 .venv/bin/python -B -m pytest tests/test_xano_pacientes_real.py -q --tb=short`.

A suíte compila o trecho de validação em grupo temporário, remove esse grupo ao terminar e inativa a Conta de Acesso fictícia criada para os testes. Não cria Pacientes nem Prontuários. Sem a flag, os testes são ignorados.

#### Idempotência e integração completa

O comprovante guarda SHA-256 do payload normalizado, sem persistir uma cópia dos campos pessoais e sem exigir configuração de chave. Essa escolha foi feita para o projeto acadêmico com dados exclusivamente fictícios. Hash sem chave não protege dados reais contra tentativa de adivinhação; não use este desenho com dados reais. A tabela `cadastro_paciente_operacao` possui índice único por Conta de Acesso e UUID. O endpoint grava Paciente, Prontuário e comprovante na mesma transação e reconsulta o resultado confirmado após uma disputa.

Essa suíte publica o endpoint completo em um grupo temporário, junto de operações auxiliares protegidas para contagens, expiração e falha de gravação. A falha é fixa no código de teste e não acrescenta parâmetros ao endpoint principal. Os testes de sucesso criam somente dados fictícios: ao terminar, Pacientes e Contas de Acesso criados pela suíte são inativados; Prontuários e comprovantes são preservados. O grupo temporário é removido. Não apagar históricos para limpar testes.

Em 27/09/2026, passaram 62 testes reais da integração temporária e o smoke test de `POST /pacientes` no grupo principal (criação e replay). A regressão local teve 196 testes aprovados. A suíte de integração é opt-in. O teste em produção cria um Paciente e uma Conta fictícios, inativa ambos ao terminar e preserva Prontuário e comprovante.

Execute a integração completa no Xano com dados fictícios:

```powershell
$env:XANO_TESTAR_PACIENTE_INTEGRACAO = "1"
.venv\Scripts\python.exe -B -m pytest tests/test_xano_pacientes_integracao.py -q --tb=short
```

No macOS, execute `XANO_TESTAR_PACIENTE_INTEGRACAO=1 .venv/bin/python -B -m pytest tests/test_xano_pacientes_integracao.py -q --tb=short`.

```powershell
.venv\Scripts\python.exe -B -m pytest tests/test_acesso.py tests/test_interface.py tests/test_profissionais.py tests/test_pacientes.py -q -p no:cacheprovider
```

No macOS, execute `.venv/bin/python -B -m pytest tests/test_acesso.py tests/test_interface.py tests/test_profissionais.py tests/test_pacientes.py -q -p no:cacheprovider`.

- [Visão do projeto](docs/project-overview.md)
- [Modelo de domínio](docs/domain-model.md)
- [Instruções de trabalho](AGENTS.md)
- [Proposta de login](openspec/changes/archive/2026-09-25-login-streamlit-xano/proposal.md)
- [Verificações e tarefas](openspec/changes/archive/2026-09-25-login-streamlit-xano/tasks.md)

O MVP utiliza somente dados fictícios e não é destinado ao uso clínico real.
