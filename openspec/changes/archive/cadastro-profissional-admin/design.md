## Context

Ver proposal.md para motivação e recorte confirmado. O projeto já possui conta_acesso, sessao_acesso, três endpoints de autenticação e validação de sessão. A função sorriso_validar_sessao valida vínculo/prazo/revogação, mas a autorização por perfil pertence ao endpoint; ela sozinha não autoriza cadastro.

A spec atual de acesso restringe a página inicial à identidade. Esta change altera explicitamente esse comportamento somente para Administrador. Não há código de Profissional versionado nessa cópia; isso não comprova ausência de estruturas legadas no Xano. A inspeção remota será requisito anterior à implementação de tabelas.

## Goals / Non-Goals

**Objetivos:** criação atômica e autorizada, reutilização da autenticação, separação entre Profissional e Conta de Acesso, interface administrativa distinta da identificação de Dentista.

**Não objetivos:** novo provedor de autenticação, senha persistida no frontend, dados clínicos, migração de legados, cadastro de outros perfis ou tela pública de pacientes. Os contratos abaixo são propostos, não endpoints já publicados.

## Decisions

### Navegação e identidade
Revalidar /auth/me antes de exibir páginas protegidas. Com administrador nos perfis retornados, apresentar Página do Administrador, identificação, Cadastrar profissional e Sair. O cadastro é uma página própria com Voltar. Sem administrador, manter identificação e saída; nenhuma página clínica será construída nesta entrega. Em contas com múltiplos perfis, a presença de administrador autoriza a página administrativa sem seletor local.

Login da equipe permanece único para os perfis internos, identificado como acesso da equipe. Não oferecer entrada ou cadastro de Paciente nesta superfície. A tela futura de Paciente terá fluxo separado, não criado agora.

Separar componentes de página, cliente REST e sessão conforme a organização existente. Escolher a API de navegação Streamlit durante Apply após verificar compatibilidade instalada, sem alterar o comportamento especificado.

### Formulário e validação proposta
Nome: texto aparado, 2 a 120 caracteres. E-mail: formato válido, até 254 caracteres, aparado e convertido a minúsculas no backend. Senha inicial: 12 a 128 caracteres, sem aparar ou transformar; campo password do Xano transforma antes de persistir. Confirmação obrigatória apenas na interface e nunca enviada. Estes limites são decisões propostas para cadastro, não alterações das regras do login existente.

CRO: texto obrigatório até 32 caracteres, formato UF-NUMERO (UF brasileira e 1 a 10 dígitos); converter UF para maiúsculas, remover espaços externos e normalizar zeros iniciais do número; recusar número zero. Unicidade pelo par UF/número normalizado. Sem consulta externa a registros profissionais; exemplos exclusivamente fictícios.

Especialidade: seleção obrigatória de registro ativo da tabela especialidade, conforme adaptação aprovada pelo usuário. GET /especialidades, exclusivo de Administrador, retorna {"especialidades":[{"id":1,"nome":"Clínica geral"}]}. Lista vazia bloqueia envio e orienta configurar especialidades no Xano; nenhuma criação automática. Não coletar CPF, RG, endereço ou telefone neste recorte. Campos futuros do domínio não são obrigatórios nesta operação. Identificador, situação ativa e datas são gerados no backend. Senhas apagadas do estado após processamento, Voltar e logout; não usar cache ou URLs para dados do formulário.

### Contrato REST proposto
POST /profissionais relativo a XANO_API_BASE_URL no grupo da equipe, com Authorization Bearer e JSON. Autenticação pela conta_acesso, validação de sessão existente, consulta atual da conta e exigência de situação ativo e perfil administrador antes de processar os dados.

Corpo estrito: nome, email, senha e cro como strings obrigatórias e especialidade_id como inteiro positivo obrigatório. O backend rejeita especialidade inexistente ou inativa com 400. Rejeitar campos extras, inclusive perfis, situacao e conta_acesso_id. Não aceitar perfil enviado pelo cliente: gerar exclusivamente ["profissional"] no backend.

201: {"profissional":{"id":123,"nome":"Dentista Ficticio","cro":"SP-123456","especialidade":{"id":1,"nome":"Clinica geral"},"situacao":"ativo"},"conta":{"id":456,"perfis":["profissional"],"situacao":"ativo"}}. Os números são ilustrativos. Não retornar senha, e-mail, hash nem token. O cliente valida tipos, IDs positivos e estrutura antes de confirmar sucesso.

400 DADOS_INVALIDOS: campos ausentes, inválidos ou extras.
401 SESSAO_INVALIDA: credencial ausente, inválida, expirada ou revogada.
403 ACESSO_NEGADO: conta inativa/bloqueada ou sem administrador.
409 CADASTRO_DUPLICADO: e-mail ou CRO já cadastrado, mensagem segura sem dados da conta existente.
429: informar espera, sem repetição automática.
5xx/timeout/resposta incompatível: mensagem local de resultado não confirmado, sem corpo técnico.
Erros controlados seguem {"codigo":"...","mensagem":"..."}; erros nativos também são sanitizados pelo cliente. Cache-Control: no-store e histórico de requisições desativado no grupo, endpoint e funções que manipulam credenciais.

### Dados e atomicidade
Conta de Acesso usa tabela existente, nome, e-mail único, senha transformada, perfis e situação. Reutilizar profissional (883768), preservando nome, cro, telefone, email, usuario_id, especialidade_id, criado_em e situacao. Acrescentar conta_acesso_id opcional/nulo para preservar legados, atualizado_em opcional e índices únicos de cro e conta_acesso_id. Novos cadastros sempre preenchem o vínculo e as datas; especialidade_id referencia especialidade (883767). Persistir Ativo/Inativo como no legado e traduzir para ativo/inativo na API. Não alterar usuario_id nem registros antigos. Não é Paciente; não cria Prontuário.

Inspecionar somente metadados de tabelas/APIs no Xano antes do Apply. Reutilizar estrutura compatível sem alterar regras legadas. Se a estrutura legada exigir migração ou modificações incompatíveis, apresentar decisão ao grupo antes de executar; não criar silenciosamente conceitos duplicados.

Criar os dois registros na mesma transação e índices únicos para e-mail, CRO e vínculo. Não confiar apenas em consulta prévia de duplicação. Conferir na instância o rollback e a tradução segura dos conflitos de índices, inclusive concorrentes. Não devolver token nem efetuar login automático, preservando a sessão do Administrador.

Não criar endpoint GET/listagem só para o formulário. Em timeout, não repetir automaticamente: a transação pode ter confirmado. Nova tentativa manual encontra unicidade e não duplica registros. Confirmar o resultado por inspeção administrativa segura durante testes; não prometer resultado remoto quando desconhecido.

## Risks / Trade-offs

- Senha inicial definida pelo Administrador → é conhecida por ele; envio ao Dentista ocorre fora da aplicação. Não há e-mail automático, convite ou alegação de senha temporária/expiração. Troca obrigatória fica para change própria.
- Duplicação concorrente → índices únicos e transação, testados na instância.
- Conta ativa antes de Profissional pronto → resposta apenas após commit e rollback integral em falhas.
- Permissões mudadas após abertura → validar novamente no backend a cada POST.
- Estrutura legada desconhecida → inspeção de metadados antes de gravar; preservar históricos.
- Mudanças locais anteriores sem diferença textual → preservar arquivos e não incluí-los por conveniência no commit.
- Purpose da spec principal de acesso contém placeholder histórico → não editar manualmente openspec/specs; não ampliar esta change para limpeza documental sem relação com o fluxo.

## Migration Plan

Criar Issue e branch vinculada a partir da main integrada, preservando mudanças locais. Revisar proposta, specs, design e tarefas antes do Apply. Inspecionar metadados, publicar estruturas/endpoint com prévia e testar no Xano com dados fictícios. Depois integrar a interface e verificar login do novo Dentista e regressão do login existente.

Em reversão, retirar a ação da interface e desabilitar a nova operação; preservar contas, profissionais e históricos criados. Não excluir tabelas legadas. Abrir PR com evidências e revisão de integrante; arquivar somente após conclusão e validação real.

## Aprovação da adaptação

Usuário aprovou Apply e, após inspeção, confirmou reutilizar a tabela profissional com seleção de especialidade existente e adição de vínculo/índices. Antes do índice, auditar apenas quantidade de CROs duplicados/não canônicos, sem expor dados; se houver conflito, interromper antes de modificar registros. Autorização da nova GET é idêntica à POST.
