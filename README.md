# Sorriso+

MVP acadêmico com Python/Streamlit na interface e Xano para autenticação, autorização e dados via API REST. Implantação pública prevista em Render ou Railway.

## Estado atual

Login, identificação da Conta de Acesso, sessão de uma hora e logout estão implementados e validados no Xano. A página protegida mostra somente nome, perfis internos e Sair. Profissional aparece como Dentista. Cadastro, recuperação de senha e funcionalidades clínicas estão fora desta entrega.

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

O [design](openspec/changes/login-streamlit-xano/design.md) detalha o contrato e as permissões. As tabelas legadas e APIs de outras funcionalidades foram preservadas.

O token fica no estado da sessão Streamlit. A identidade é revalidada antes da exibição protegida. A sessão tem prazo absoluto de uma hora, sem renovação. O logout sempre limpa o estado local e informa quando não confirmou a revogação remota. Nova conexão sem estado exige novo login.

## Testar

```powershell
.venv/Scripts/python -m pytest tests/test_acesso.py tests/test_interface.py -q
openspec validate login-streamlit-xano --strict
```

Em 23/09/2026, **54 testes locais e 25 testes reais passaram**. Os testes locais verificam configuração, contrato, falhas de rede, erros seguros e comportamento da interface. A suíte real verifica diretamente no Xano campos, perfis, contas bloqueadas/inativas, identidade própria, revogação, replay, logout repetido, perda de acesso, sessões independentes e expiração efetiva.

Para repetir os testes reais, configure `XANO_API_BASE_URL`, `XANO_WORKSPACE_ID` e `XANO_METADATA_TOKEN` no ambiente. O token administrativo deve vir de uma fonte segura e nunca ser salvo no repositório.

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

- [Visão do projeto](docs/project-overview.md)
- [Modelo de domínio](docs/domain-model.md)
- [Instruções de trabalho](AGENTS.md)
- [Proposta de login](openspec/changes/login-streamlit-xano/proposal.md)
- [Verificações e tarefas](openspec/changes/login-streamlit-xano/tasks.md)

O MVP utiliza somente dados fictícios e não é destinado ao uso clínico real.
