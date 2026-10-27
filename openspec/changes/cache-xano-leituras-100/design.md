## Contexto
O Streamlit reexecuta páginas a cada interação e a navegação pode voltar a consultar o Xano. As respostas podem conter informações pessoais ou clínicas e ficam somente no estado isolado da sessão.

## Decisões
- `sorrisomais.cache_xano` expõe `carregar_cache(state, token, namespace, loader, force=False)` e `invalidar_cache(state, namespaces=None)`.
- A chave usa SHA-256 do token e namespace; token bruto não fica em chave, valor ou log. O cache reside apenas em `session_state`.
- Não há TTL nem pré-carregamento. Um acerto permanece até force, invalidação, troca de identidade, erro 401/403 ou limpeza da sessão.
- O loader executa em falta ou force. Somente retorno bem-sucedido validado pelo cliente da rota é guardado. Exceções propagam; 401/403 limpam os dados privados.
- Force remove o valor anterior antes de tentar a rede; uma falha não deixa dado antigo parecer atualizado.
- Cada namespace inclui os parâmetros do GET, como datas e identificadores.
- Mutação bem-sucedida invalida o recurso e suas dependências. Atualização manual força a leitura da página, sem carregar outras categorias.
- Logout e expiração limpam valores e hash de escopo. Troca de Conta de Acesso ou perfil também limpa o cache.
- Cadastro de Paciente usa o contrato do helper por integração paralela da Issue 99.

## Invalidadores por dependência
- Profissional: `profissionais`, `especialidades` e `agenda/opcoes`.
- Disponibilidade: `disponibilidades`, `consultas` e `agenda/opcoes`.
- Consulta: `consultas`, `disponibilidades`, `agenda/opcoes`, `procedimentos-consulta`, `exames` e `registros-clinicos`.
- Registro Clínico: `registros-clinicos` e `consultas`.
- Exame: `exames` e `registros-clinicos`.
- Procedimento: `procedimentos`, `agenda/opcoes` e `procedimentos-consulta`.
- Paciente: `pacientes`, `paciente:<id>`, `agenda/opcoes` e `consultas` (integração da Issue 99).
- Atualização manual força o GET da tela e dos filtros exibidos.

## Inventário de cobertura

| Rota GET | Páginas/consumidores Streamlit | Namespace |
|---|---|---|
| `/especialidades` | Formulário de Profissional | `especialidades` |
| `/profissionais` | Lista de Profissionais | `profissionais` |
| `/agenda/opcoes` (inclui Pacientes, Profissionais e Procedimentos) | Agenda, Nova Consulta, Reagendamento, Exames, catálogo de Procedimentos e Painel Administrativo | `agenda/opcoes` |
| `/disponibilidades` | Agenda, Nova Consulta e Reagendamento | `disponibilidades:<filtros>` |
| `/consultas` | Agenda, painéis, Consultas do Paciente, Prontuário, Exames e Reagendamento | `consultas:<filtros>` |
| `/registros-clinicos` | Prontuário e Autoatendimento | `registros-clinicos` |
| `/exames` | Exames e Autoatendimento | `exames` |
| `/consultas/{id}/procedimentos` | Procedimentos de uma Consulta | `procedimentos-consulta:<id>` |
| `/contas-acesso` | Contas de Acesso | `contas-acesso` |
| `/pacientes` | Cadastro de Paciente, integração paralela | `pacientes` |
| `/pacientes/{id}` | Detalhe do cadastro de Paciente, integração paralela | `paciente:<id>` |

`/auth/me` permanece sem cache para detectar revogação e expiração. A cobertura fica completa após incorporar a integração da Issue 99. Testes locais usam mocks e não fazem chamadas à rede.

## Riscos
Cache sem TTL pode ficar desatualizado quando outra Conta de Acesso altera dados, até uma atualização manual. Mutações nesta sessão invalidam as dependências documentadas. O Xano continua autorizando as operações.
