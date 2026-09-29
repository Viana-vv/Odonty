# Sorriso+

MVP acadêmico com Python/Streamlit na interface e Xano para autenticação, autorização e dados via API REST. Implantação pública prevista em Render ou Railway.

## Estado atual

Login, identificação da Conta de Acesso, sessão de uma hora e logout estão implementados e validados no Xano. Administrador também pode cadastrar profissionais; Profissional aparece como Dentista. O cadastro de pacientes está disponível para Administrador e Recepcionista, com autorização aplicada no Xano. Recuperação de senha e funcionalidades clínicas permanecem fora desta entrega.

As telas existentes de login, início da equipe e cadastros de Paciente e Profissional usam a identidade visual Sorriso+ e o mascote local `assets/1000323602.jpg`. A navegação exibe somente ações disponíveis para o perfil autenticado; módulos que ainda não possuem fluxo não aparecem como opções.

Issue: [#1](https://github.com/Viana-vv/Odonty/issues/1). Implementação na branch `feat/1-login-streamlit-xano`, preparada para revisão do grupo.

## Executar localmente

Use Python 3.10 ou superior. No PowerShell, a partir da raiz:

```powershell
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements-dev.txt
$env:XANO_API_BASE_URL = "https://sua-instancia.xano.io/api:seu-grupo"
$env:XANO_HTTP_TIMEOUT_SECONDS = "10"
.venv/Scripts/python -m streamlit run app.py
```

Abra **http://localhost:8501**. Substitua o endereço ilustrativo pela URL HTTPS do grupo publicado. Para executar sem ferramentas de teste, instale `requirements.txt`.

O grupo validado nesta entrega é `https://x8ki-letl-twmt.n7.xano.io/api:sorriso-acesso:v1`. A URL foi configurada como variável de ambiente do usuário Windows nesta máquina. Novos terminais herdam essa configuração; em outra máquina, defina-a antes de iniciar o Streamlit.

O arquivo `.env.example` é uma referência: a aplicação não carrega `.env` automaticamente. Credenciais administrativas do Xano não são credenciais de login e não devem ser usadas no frontend.

| Variável | Ambiente | Configuração |
|---|---|---|
| `XANO_API_BASE_URL` | Streamlit | Obrigatória; HTTPS, sem credenciais, query string ou fragmento |
| `XANO_HTTP_TIMEOUT_SECONDS` | Streamlit | Opcional; número positivo e finito, padrão 10 segundos |
| `XANO_CADASTRO_PACIENTE_HABILITADO` | Streamlit | Opcional; habilitado por padrão após publicação e validação do endpoint; definir `0` para ocultar a ação |
| `AUTH_SESSION_TTL_SECONDS` | Xano | Padrão 3600 segundos; valores menores somente em testes isolados |

Sem configuração válida, a tela informa o problema e desabilita o formulário.

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

O [design](openspec/changes/archive/2026-09-25-login-streamlit-xano/design.md) detalha o contrato e as permissões. As tabelas legadas e APIs de outras funcionalidades foram preservadas.

O token fica no estado da sessão Streamlit. A identidade é revalidada antes da exibição protegida. A sessão tem prazo absoluto de uma hora, sem renovação. O logout sempre limpa o estado local e informa quando não confirmou a revogação remota. Nova conexão sem estado exige novo login.

## Testar

```powershell
.venv/Scripts/python -m pytest tests/test_acesso.py tests/test_interface.py -q
openspec validate --all --strict
```

Em 23/09/2026, **54 testes locais e 25 testes reais passaram**. Os testes locais verificam configuração, contrato, falhas de rede, erros seguros e comportamento da interface. A suíte real verifica diretamente no Xano campos, perfis, contas bloqueadas/inativas, identidade própria, revogação, replay, logout repetido, perda de acesso, sessões independentes e expiração efetiva.

Para repetir os testes reais, configure `XANO_API_BASE_URL`, `XANO_METADATA_BASE_URL`, `XANO_WORKSPACE_ID` e `XANO_METADATA_TOKEN` no ambiente. O token administrativo deve vir de uma fonte segura e nunca ser salvo no repositório.

Para inspeção de tabelas, schemas e demais chamadas da Metadata API, use `XANO_METADATA_BASE_URL=https://x8ki-letl-twmt.n7.xano.io/api:meta` com `Authorization: Bearer` usando `XANO_METADATA_TOKEN`. Acrescente `/workspace/{XANO_WORKSPACE_ID}` para operações do workspace. Não derive esse endereço de `XANO_API_BASE_URL`, que aponta exclusivamente para o grupo de API do projeto. Skills e ferramentas de inspeção devem seguir essa mesma separação.

```powershell
$env:XANO_TESTAR_REAL = "1"
.venv/Scripts/python -m pytest tests/test_xano_real.py -q --tb=short
```

Sem a opção explícita, os testes reais são ignorados. A suíte cria somente contas fictícias, com senhas aleatórias transformadas pelo campo password do Xano, e as inativa ao terminar. O teste de expiração cria um grupo temporário com validade de oito segundos e o remove em `finally`; o grupo principal permanece com uma hora. Nenhuma verificação depende de ignorar o prazo ou alterar o relógio.

As chamadas da suíte são espaçadas para respeitar o limite do plano Xano. HTTP 429 pode prolongar a execução. A aplicação não repete automaticamente login ou logout.

Também foram verificados: computador (1440 px), tablet (768 px), celular (390 px), ausência de rolagem horizontal, foco de teclado, senha mascarada, uma única chamada após clique duplo e bloqueio do formulário durante o envio. O fluxo completo navegador → Streamlit → Xano foi confirmado com entrada, identidade e saída.

Os três endpoints usam `history = false`; o histórico do grupo permaneceu vazio após os testes. Evidências locais sem credenciais ficam em `test-results/`, ignorado pelo Git.

## Acesso fictício nesta máquina

A credencial de demonstração foi protegida pelo Windows em `test-results/acesso-teste.clixml`, fora do Git. Somente o usuário Windows que a criou pode recuperá-la:

```powershell
(Import-Clixml .\test-results\acesso-teste.clixml).GetNetworkCredential() | Format-List UserName,Password
```

Esse arquivo não acompanha o repositório. Em outra máquina, um responsável deve preparar uma Conta de Acesso fictícia no Xano. Não reutilize senhas pessoais.

## Documentação

### Cadastro de pacientes — implementação local

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
.venv/Scripts/python -B -m pytest tests/test_xano_pacientes_real.py -q --tb=short
```

A suíte compila o trecho de validação em grupo temporário, remove esse grupo ao terminar e inativa a Conta de Acesso fictícia criada para os testes. Não cria Pacientes nem Prontuários. Sem a flag, os testes são ignorados.

#### Idempotência e integração completa

O comprovante guarda SHA-256 do payload normalizado, sem persistir uma cópia dos campos pessoais e sem exigir configuração de chave. Essa escolha foi feita para o projeto acadêmico com dados exclusivamente fictícios. Hash sem chave não protege dados reais contra tentativa de adivinhação; não use este desenho com dados reais. A tabela `cadastro_paciente_operacao` possui índice único por Conta de Acesso e UUID. O endpoint grava Paciente, Prontuário e comprovante na mesma transação e reconsulta o resultado confirmado após uma disputa.

Essa suíte publica o endpoint completo em um grupo temporário, junto de operações auxiliares protegidas para contagens, expiração e falha de gravação. A falha é fixa no código de teste e não acrescenta parâmetros ao endpoint principal. Os testes de sucesso criam somente dados fictícios: ao terminar, Pacientes e Contas de Acesso criados pela suíte são inativados; Prontuários e comprovantes são preservados. O grupo temporário é removido. Não apagar históricos para limpar testes.

Em 27/09/2026, passaram 62 testes reais da integração temporária e o smoke test de `POST /pacientes` no grupo principal (criação e replay). A regressão local teve 196 testes aprovados. A suíte de integração é opt-in. O teste em produção cria um Paciente e uma Conta fictícios, inativa ambos ao terminar e preserva Prontuário e comprovante.

Execute a integração completa no Xano com dados fictícios:

```powershell
$env:XANO_TESTAR_PACIENTE_INTEGRACAO = "1"
.venv/Scripts/python -B -m pytest tests/test_xano_pacientes_integracao.py -q --tb=short
```

```powershell
.venv/Scripts/python -B -m pytest tests/test_acesso.py tests/test_interface.py tests/test_profissionais.py tests/test_pacientes.py -q -p no:cacheprovider
```

- [Visão do projeto](docs/project-overview.md)
- [Modelo de domínio](docs/domain-model.md)
- [Instruções de trabalho](AGENTS.md)
- [Proposta de login](openspec/changes/archive/2026-09-25-login-streamlit-xano/proposal.md)
- [Verificações e tarefas](openspec/changes/archive/2026-09-25-login-streamlit-xano/tasks.md)

O MVP utiliza somente dados fictícios e não é destinado ao uso clínico real.
