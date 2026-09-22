## Context

Esta é a proposta técnica solicitada pelo usuário para revisão, não um contrato já publicado no Xano. Estão aprovados: login por e-mail e senha, página inicial com nome, perfil e Sair, três perfis internos e o rótulo Dentista para Profissional. Os detalhes abaixo ainda dependem da revisão desta proposta antes de Apply.

Não há protótipo React/Vinext disponível, conforme confirmação do usuário. Não existem endpoints comprovados nesta sessão. A conexão anterior com a instância terminou em timeout; isso não comprova indisponibilidade permanente. O login administrativo do CLI não é autenticação da aplicação.

## Goals / Non-Goals

**Objetivos:** definir contrato verificável para login, identidade, sessão, autorização inicial e logout usando Streamlit/Python e Xano via REST.

**Não objetivos:** acesso clínico, cadastro, recuperação de senha, administração de contas pela interface, renovação automática, Drizzle/D1 ou persistência de negócio em localStorage. Não alterar as permissões conceituais de outras funcionalidades do domínio.

## Decisions

### Arquitetura proposta

Navegador → Streamlit/Python → Xano. Separar interface, configuração, cliente REST e controle de sessão. Manter o token somente no estado de sessão isolado no servidor Streamlit, sem cache global, cookies próprios, URLs ou armazenamento no navegador. Limpar a senha do estado do formulário após o envio. Não armazenar credenciais de administração do Xano na aplicação.

A documentação oficial descreve autenticação de endpoints por token, validação de senha e informações adicionais no token. Consultar perfis atuais na Conta de Acesso em cada operação evita depender de permissões antigas guardadas no token. Referências: [autenticação](https://docs.xano.com/building-backend-features/user-authentication-and-user-data) e [autorização por perfil](https://docs.xano.com/building-backend-features/user-authentication-and-user-data/restricting-access-rbac).

As rotas, campos, tabelas e duração abaixo são decisões propostas para o Sorriso+, não padrões presumidos nem recursos já configurados. A implementação deve verificar o suporte na instância e ajustar a proposta se necessário.

### Contrato REST proposto

Rotas relativas a `XANO_API_BASE_URL`, que deverá conter a URL HTTPS real do grupo de APIs. JSON em UTF-8; `Content-Type: application/json` nos corpos. Respostas de autenticação com `Cache-Control: no-store`. Nas operações autenticadas: `Authorization: Bearer <token>`. O token é opaco para o frontend; não decodificar como JWT para inferir permissões ou validade.

| Operação | Entrada | Sucesso |
|---|---|---|
| POST /auth/login | Objeto com somente email e senha, ambos strings obrigatórias | 200 com token, tipo_token e expira_em |
| GET /auth/me | Bearer; sem corpo, identificador de conta ou parâmetros | 200 com conta e expira_em |
| POST /auth/logout | Bearer; sem corpo ou identificador de sessão enviado pelo cliente | 204 sem corpo após revogar a sessão identificada pelo token |

**Login:** remover espaços externos e normalizar caixa do e-mail no backend e na criação das contas fictícias; validar formato. Senha não deve ser aparada nem transformada. E-mail ou senha ausente, e-mail inválido ou campos extras como perfil produzem 400. Não estabelecer regra de complexidade de senha no login. Verificar senha pelo mecanismo do Xano, situação ativa e pelo menos um perfil interno permitido antes de emitir token.

Contrato de sucesso de login (valores descritivos, não credenciais):

```json
{"token":"<token opaco emitido pelo Xano>","tipo_token":"Bearer","expira_em":"2026-10-01T15:00:00Z"}
```

`expira_em` é string de data/hora UTC em RFC 3339, emitida pelo backend e correspondente à validade do token e da sessão. Após receber o token, a interface consulta /auth/me; somente após validar essa resposta pode apresentar a página protegida. Falha nessa consulta não estabelece uma sessão autenticada na interface.

Contrato de sucesso de /auth/me, com dados fictícios:

```json
{"conta":{"id":101,"nome":"Pessoa de Teste","perfis":["profissional"],"situacao":"ativo"},"expira_em":"2026-10-01T15:00:00Z"}
```

`id`: inteiro positivo; `nome`: string não vazia; `perfis`: lista sem duplicatas com valores do domínio (administrador, recepcionista, profissional, paciente); `situacao`: ativo para respostas bem-sucedidas. A lista precisa conter ao menos um perfil interno. A interface exibe apenas os perfis internos retornados, com rótulos Administrador, Recepcionista e Dentista, em ordem estável. Contas com vários perfis internos usam a mesma página, sem seleção nem elevação de privilégio. Uma conta somente com perfil paciente não acessa esta aplicação interna.

O Xano identifica a conta exclusivamente pela credencial validada. /auth/me não permite consultar outras contas. Senha, e-mail, identificadores de Paciente/Profissional e dados clínicos não são retornados.

**Erros controlados:** objeto `{"codigo":"CODIGO","mensagem":"Mensagem segura em português."}`. O cliente não apresenta corpo técnico bruto e possui mensagens próprias para códigos conhecidos. Proxies ou erros nativos do Xano podem ter outro formato: tratar como falha de integração sem exibir o corpo.

| HTTP | Código proposto | Tratamento |
|---|---|---|
| 400 | DADOS_INVALIDOS | Orientar correção, sem sessão |
| 401 no login | CREDENCIAIS_INVALIDAS | Mesma resposta para conta inexistente, senha incorreta e conta bloqueada/inativa; não revelar qual ocorreu |
| 401 nas rotas protegidas | SESSAO_INVALIDA | Token ausente, inválido, expirado, revogado ou sessão inexistente; limpar estado e pedir nova entrada |
| 403 | ACESSO_NEGADO | Conta sem perfil interno; nas rotas protegidas também conta bloqueada/inativa; retirar conteúdo e limpar estado |
| 429, caso retornado | MUITAS_TENTATIVAS | Informar espera, sem repetição automática |
| 5xx, resposta inválida, timeout | Falha de serviço | Mensagem local de indisponibilidade; não liberar acesso nem exibir detalhes |

Em /auth/logout, um token válido de sessão já revogada retorna 204 (idempotência). Token expirado ou inválido retorna 401; a interface considera que não há sessão válida a manter. Logout não depende de perfil interno nem situação ativa, para permitir encerramento mesmo após perda de acesso. Ainda exige token validado e vínculo entre sessão e conta.

### Dados e revogação propostos no Xano

Antes de criar tabelas, inspecionar se existe estrutura compatível e reutilizá-la sem sobrescrever dados. Proposta física mínima:

- `conta_acesso`: id, nome, email único normalizado, senha em campo próprio de senha do Xano, perfis como lista de valores do domínio e situacao. Habilitar autenticação nessa tabela. Não criar associação com Paciente para este login.
- `sessao_acesso`: id aleatório único, conta_acesso_id, criada_em, expira_em e revogada_em opcional. Não guardar o token nem a senha nessa tabela.

No login, emitir token com validade de 3600 segundos e `sessao_id` nos extras, associado à conta; gravar a sessão correspondente. Se qualquer etapa falhar, não devolver token utilizável. Endpoints protegidos validam autenticação nativa, existência da sessão, titularidade, prazo, ausência de revogação, conta ativa e perfil permitido. Reutilizar essa validação no backend. O logout marca somente a sessão atual como revogada; outras sessões da mesma conta permanecem válidas. Não excluir históricos.

A revogação é lógica proposta da aplicação: limpar o estado Streamlit sozinho não revoga um token. A tabela de sessões foi escolhida para suportar revogação independente sem trocar a senha nem encerrar todas as sessões. A alternativa de logout somente local deixa a credencial utilizável até expirar e não é a opção recomendada.

Configurar o histórico de requisições e logs do Xano e do frontend para não registrar senha, Authorization ou token de resposta. Verificar isso antes de testar credenciais, mesmo fictícias. Não presumir que a configuração padrão já elimina esses campos.

### Política de sessão proposta

- Duração absoluta de uma hora a partir do login, sem extensão por atividade ou refresh token.
- O Xano é a autoridade de validade; a interface usa expira_em para antecipar o retorno ao login e revalida /auth/me antes de apresentar conteúdo protegido em cada execução da página.
- Nova aba, recarga que reconstrua a sessão ou reinício do Streamlit exige nova entrada; sem opção Lembrar de mim. O registro remoto anterior expira no prazo, sem promessa de revogação ao fechar o navegador.
- Logout chama o backend antes de limpar o token e sempre limpa o estado local, inclusive em timeout. Em falha de rede, mostrar: “Você saiu deste acesso, mas não foi possível confirmar o encerramento no servidor. A sessão expira em até uma hora.” Não afirmar revogação remota sem confirmação.
- Em indisponibilidade durante revalidação, não apresentar identidade em cache: limpar estado autenticado, informar indisponibilidade e permitir nova tentativa de login.
- A interface não retenta automaticamente login ou logout, evitando efeitos duplicados. Sessão remota criada sem resposta ao cliente expira normalmente.

Uma hora reduz a complexidade do MVP sem introduzir refresh tokens. É uma proposta de produto, não uma exigência nem um padrão do Xano.

### Matriz proposta somente para esta change

Todas as permissões abaixo exigem Conta de Acesso ativa e sessão válida. A verificação pertence ao Xano.

| Operação | Administrador | Recepcionista | Profissional (Dentista) | Somente Paciente |
|---|---|---|---|---|
| Entrar na aplicação interna | Sim | Sim | Sim | Não |
| Ver próprio nome e perfis internos | Sim | Sim | Sim | Não |
| Encerrar própria sessão | Sim | Sim | Sim | Sim, se já possuir token válido, mesmo após perda de acesso |
| Consultar identidade de outra conta | Não | Não | Não | Não |

Não criar endpoints de administração, prontuários, consultas ou exames nesta change. Esta matriz não retira permissões conceituais futuras do domínio nem concede acesso clínico ao Administrador. Perfis desconhecidos não concedem acesso; nenhuma escolha no formulário altera perfis.

### Configuração proposta

- Frontend: `XANO_API_BASE_URL` obrigatória, HTTPS, sem token, query string ou fragmento; `XANO_HTTP_TIMEOUT_SECONDS` opcional, padrão 10, valor positivo. Validar configuração antes de permitir submissão. Não repetir automaticamente requisições após timeout.
- Backend: `AUTH_SESSION_TTL_SECONDS=3600`; uma mudança nesse valor requer atualizar a política e os testes. O frontend recebe o prazo do backend, sem configurá-lo independentemente.
- Nenhum segredo administrativo necessário no frontend. Dependências Python e comando de execução serão documentados ao implementar; não há aplicação executável nesta etapa.

### Referência visual

A imagem 1000323602.jpg mostra mascote de dente sorridente, escova, creme dental, contornos escuros, detalhes azuis e fundo branco. Os textos NOME DA CLÍNICA e TAGLINE AQUI são placeholders.

Usar mascote com Sorriso+ e formulário lado a lado no computador e disposição vertical em telas pequenas. Verde nos elementos de ação, fundo claro, rótulos visíveis e foco de teclado. Preparar asset sem placeholders preservando o original. Nenhuma imagem foi editada nesta etapa.

### Critérios de verificação

Simulação: validar campos, resposta vazia/malformada, formatos de identidade e expiração, timeout, 400/401/403/429/5xx, isolamento entre sessões e mensagens sem segredos. Não confundir esses resultados com integração.

Xano real: contas fictícias dos três perfis e múltiplos perfis, somente paciente, bloqueada/inativa; login válido/inválido; token ausente/adulterado; tentativa de consultar outra conta; expiração; revogação; replay do token após logout; logout repetido; logout de conta que perdeu acesso; segunda sessão preservada; falha de rede durante logout. Para expiração, usar configuração curta somente em ambiente isolado de teste e restaurar 3600 antes da verificação final. Nunca ignorar validade no teste que comprova expiração.

Verificar proteção sem depender da interface. Revisar logs para ausência de credenciais, sem copiá-las para evidências. Na interface, testar computador/tablet/celular, teclado, envio em andamento, duplicação, erros e retorno após logout. Registrar ambiente, data, esperado/obtido e se real ou simulado. Integração indisponível permanece bloqueada.

## Risks / Trade-offs

- Revogação requer consulta à sessão em cada operação → custo adicional pequeno e necessário ao logout proposto.
- Sem persistência após recarga → exige novo login, mas evita mecanismo adicional de armazenamento de credenciais.
- Falha de rede no logout → saída local garantida; revogação remota não garantida até expiração, explicitada ao usuário.
- Configuração real não inspecionada → verificar suporte, rotas existentes e logs antes de implementar; atualizar proposta se divergente.
- Contratos e política ainda em revisão → não publicar endpoints nem declarar integração funcional nesta etapa.

## Migration Plan

Após revisão, vincular Issue e branch, inspecionar o Xano, implementar tabelas e endpoints aprovados, validar os contratos reais e integrar Streamlit. Não modificar tabelas clínicas nem ativar outro banco. Abrir PR com testes e revisão de integrante. Reverter apenas componentes introduzidos, preservando dados e históricos. Archive somente após validação real e todas as tarefas concluídas. Os quatro documentos presentes não significam implementação concluída.

## Aprovação e inspeção para Apply

Contrato, política e matriz aprovados pelo usuário nesta conversa. Após inspeção, o usuário autorizou criar estruturas separadas e preservar usuario (autenticação desativada, perfil único e estado booleano) e todas as APIs antigas. Issue: https://github.com/Viana-vv/Odonty/issues/1. Branch: feat/1-login-streamlit-xano. A aprovação substitui as indicações anteriores de pendência de revisão; ainda é necessária a validação real da implementação.
