## Context

Ver proposal.md para motivação e recorte. O projeto separa interface, cliente REST e sessão; o backend dispõe de conta_acesso e sorriso_validar_sessao. A página atual distingue Administrador dos demais perfis e possui cadastro de Profissional em andamento. Não há definição local de Paciente ou Prontuário; ausência de arquivos não comprova ausência de tabelas legadas no Xano.

## Goals / Non-Goals

Garantir criação atômica, autorização atual por operação e reenvio seguro sem misturar Paciente com identidade de login. Reutilizar as camadas existentes e adicionar módulo de paciente, evitando expandir as regras específicas de profissionais. Não migrar registros legados nem criar permissões clínicas nesta entrega.

## Decisions

### Campos e validação

Decisão aprovada: todos os campos do formulário são obrigatórios.

| Campo | Regra |
|---|---|
| nome | Obrigatório, aparar espaços externos, 2 a 120 caracteres |
| data_nascimento | Obrigatória, data real em YYYY-MM-DD, de 0001-01-01 até a data corrente em America/Sao_Paulo |
| cpf | Obrigatório; aceitar 11 dígitos ASCII ou máscara XXX.XXX.XXX-XX, normalizar para dígitos, validar verificadores e rejeitar sequências repetidas |
| email | Obrigatório; aparar, converter para minúsculas, formato válido, até 254 caracteres |
| telefone | Obrigatório; aceitar número nacional de 10 ou 11 dígitos ASCII e máscara com espaços, parênteses e hífen; persistir somente dígitos; contato compartilhado é permitido |
| celular | Obrigatório; aceitar número nacional de 10 ou 11 dígitos ASCII e máscara com espaços, parênteses e hífen; persistir dígitos; não consultar serviços externos |

RG, gênero e endereço ficam para ampliação do cadastro. Telefone, e-mail e celular não são únicos: familiares podem compartilhar contato. Nome e nascimento não identificam unicamente uma pessoa; homônimos são permitidos. CPF é obrigatório nesta change e deve ser único. Usar exemplos exclusivamente sintéticos; validação matemática não comprova identidade.

### Autorização e navegação

Revalidar /auth/me antes de renderizar. Administrador mantém cadastro de Profissional e recebe Cadastrar paciente; Recepcionista recebe Cadastrar paciente; Profissional sem esses perfis mantém identificação e Sair. Usar a presença de qualquer perfil permitido, sem seletor de perfil. Campos e estado do paciente usam prefixo próprio para não colidir com cad_* de profissionais. Limpar ambos no logout e na perda de sessão. Voltar limpa somente o formulário abandonado.

O POST autentica pela conta_acesso, valida sessão e consulta situação/perfis atuais antes de processar dados ou responder a um reenvio. Ter prontuário criado automaticamente não autoriza Recepcionista a ler ou escrever conteúdo clínico.

### Contrato REST

POST /pacientes relativo à configuração existente, Authorization Bearer e JSON estrito: nome, data_nascimento, telefone, cpf, email, celular, operacao_id. Todos os seis campos cadastrais são strings obrigatórias e não podem estar ausentes, null ou vazios; operacao_id é UUID v4 obrigatório gerado pela interface. Rejeitar tipos incorretos, booleanos usados como identificadores e campos extras, inclusive conta_acesso_id, situacao, perfis ou conteúdo clínico.

201, inclusive em replay concluído da mesma operação: {"paciente":{"id":123,"nome":"Paciente Fictício","situacao":"ativo"},"operacao_id":"UUID-da-operação"}. IDs são ilustrativos. O cliente confere ID inteiro positivo, nome normalizado, situação e operação antes de confirmar. Não retornar CPF, nascimento, contatos ou dados do prontuário.

400 DADOS_INVALIDOS; 401 SESSAO_INVALIDA; 403 ACESSO_NEGADO; 409 CPF_DUPLICADO ou OPERACAO_CONFLITANTE; 429 limite de chamadas; 503 falha sem confirmação. Mensagens controladas e seguras, sem corpo técnico. O cliente distingue os dois códigos conhecidos de 409 por lista permitida e não reutiliza a mensagem de duplicação de CRO do cadastro profissional. Cache-Control: no-store; histórico desativado nos endpoints e funções que recebem dados cadastrais. Não adicionar listagem para sustentar este formulário.

### Persistência e criação integral

Inspecionar metadados do Xano antes de definir nomes físicos e versionar o mapeamento. Reutilizar tabelas compatíveis que representem Paciente e Prontuário; não presumir que usuario legado equivale a Paciente. Se não houver estruturas compatíveis, criar as entidades do domínio; migração incompatível ou alteração de registros existentes exige decisão específica antes de executar.

Paciente: identificador, seis campos cadastrais, situação ativa, criação e atualização geradas no backend; nenhuma conta criada ou vinculada por este POST. Prontuário: identificador, paciente_id obrigatório e único, abertura e situação ativa, sem registros clínicos. Índice único sobre CPF, que é obrigatório. Auditar apenas contagens de conflitos antes de adicionar índices a legados; não corrigir dados automaticamente.

Gravar Paciente, Prontuário e comprovante de operação dentro de uma transação. Índices asseguram unicidade; consultas prévias são apenas para mensagens amigáveis. Falha em qualquer gravação deve reverter todas. Validar transação e semântica de null na instância; testes simulados não comprovam essas garantias.

### Mapeamento inspecionado e adaptação aprovada — 27/09/2026

- Metadata API autenticada com HTTP 200 usando o token atualizado do ambiente persistente do usuário e XANO_METADATA_BASE_URL.
- Paciente corresponde à tabela paciente (883766), com telefone obrigatório. O usuário determinou manter telefone obrigatório. Reutilizar esse campo, preservar os valores existentes e acrescentar celular obrigatório, em coluna própria; não permitir cadastro sem telefone nem inventar um valor para satisfazer a restrição.
- A tabela legada prontuario (883771) exige profissional, procedimento, data de registro e observações: representa registros de atendimento, não o Prontuário único vazio do domínio.
- O usuário aprovou preservar integralmente prontuario e criar prontuario_paciente (publicada com ID 899868) para o conceito de Prontuário, com paciente_id obrigatório e único, aberto_em e situacao. Não migrar ou vincular automaticamente registros clínicos legados nem criar prontuários retroativos nesta change.
- A nova operação pertence ao grupo Sorriso Acesso (434156), preservando as operações existentes.

### Idempotência para cadastros

Apenas bloquear o botão ou usar CPF único não protege todos os cadastros após timeout. Adotar registro interno de operação com conta solicitante, UUID, impressão dos campos normalizados e paciente_id; unicidade composta de solicitante e UUID. Por decisão do usuário para este projeto acadêmico com dados exclusivamente fictícios, usar SHA-256 da serialização canônica dos seis campos, sem chave adicional. Hash sem chave não é adequado para proteger dados reais contra adivinhação.

Consultar operação concluída após autenticar e normalizar. Mesma chave e mesma impressão retornam o resultado persistido; conteúdo diferente retorna OPERACAO_CONFLITANTE. Requisições concorrentes disputam índice único dentro da transação; a perdedora reverte e reconsulta o comprovante confirmado antes de responder. Sem resultado confirmado, devolver indisponibilidade segura. O registro não usa estado "em andamento" persistido fora da transação, evitando reservas órfãs. Preservar comprovantes nesta entrega; limpeza/rotação futura precisa manter a garantia de replay.

Interface gera chave ao abrir um cadastro e mantém o payload de uma operação com resultado incerto. Não repete automaticamente. Após timeout ou resposta incompatível, oferece reenvio manual do mesmo payload, sem permitir alterá-lo até confirmar o resultado; Voltar continua disponível e limpa o estado local, com aviso de que sair não desfaz cadastro possivelmente concluído. Após rejeição definitiva por validação ou CPF duplicado, permite corrigir e gera nova chave. Após sucesso, limpa os campos e gera nova chave. Reinício/perda de sessão não recupera o formulário: a garantia de replay depende da mesma chave; nova operação pode representar a mesma pessoa e exige conferência administrativa em caso de dúvida.

### Testes

Testes locais com API simulada cobrem contratos, campos, navegação e sessão. Testes reais opt-in cobrem permissões, índices, campos obrigatórios, transação, replay e concorrência. Falha induzida de gravação deve ocorrer em operação de teste isolada com a mesma lógica, sem publicar parâmetros de falha na API de produção. Usar somente dados fictícios; preservar registros e históricos, inativando as entidades de teste ao final conforme regras do projeto. Inspecionar respostas/históricos sem imprimir tokens ou dados pessoais.

## Risks / Trade-offs

- Cadastro anterior ainda em andamento → preservar seus comportamentos e conciliar deltas antes do arquivo das changes.
- Tabelas legadas desconhecidas → inspecionar metadados antes de mutações e registrar mapeamento.
- Campos pessoais não substituem a chave de operação → idempotência protege a mesma operação, sem prometer deduplicação por identidade.
- Resultado incerto e perda do estado local → mensagem explícita e conferência administrativa, sem repetição automática.
- Dados pessoais em histórico/cache → desativar histórico, respostas mínimas e estado isolado por sessão.
- Dependências locais ausentes → preparar ambiente isolado antes dos testes; não interpretar resultado histórico como validação atual.

## Migration Plan

A interface fica desabilitada por padrão até a publicação e verificação do backend. Após essa verificação, definir `XANO_CADASTRO_PACIENTE_HABILITADO=1` no ambiente Streamlit. Essa configuração apenas controla a disponibilização; não substitui autenticação e autorização no Xano.

Após revisão, criar Issue e branch vinculada, inspecionar metadados e preparar scripts compatíveis. Publicar tabelas, índices, configuração secreta de idempotência e endpoint antes de habilitar a interface. Executar testes reais e locais, atualizar README e abrir PR com evidências. Reversão: retirar a ação e desabilitar a nova operação, preservando Pacientes, Prontuários e comprovantes já criados. Não arquivar enquanto validações ou revisão estiverem pendentes. O TBD preexistente da spec principal é pendência separada; não alterá-la manualmente nesta change.

### Correções verificadas — 27/09/2026

- Auditoria protegida retornou somente contagens: tabela Paciente vazia, sem CPF duplicado, ausente ou fora da normalização. Nenhum cadastro existente foi alterado.
- Criado e relido o índice único de paciente.cpf (5b24926c). Adicionados situacao (ativo/inativo) e atualizado_em; schema remoto exportado para backend/xano/table/paciente.xs. As colunas aceitam null para compatibilidade com estruturas legadas; o novo POST exige os seis campos e define explicitamente situação ativa e datas de criação/atualização.
- O endpoint versionado calcula os dois verificadores do CPF, rejeita máscara fora do formato e valida o calendário gregoriano, inclusive anos bissextos e o limite de hoje em America/Sao_Paulo.
- O trecho de validação foi compilado e executado no Xano em grupo temporário autenticado, interrompendo antes da persistência. Essa verificação não equivale à publicação nem ao teste da transação/idempotência do endpoint completo.

### Preparação da idempotência — 27/09/2026

- Publicada cadastro_paciente_operacao (900060), com referências obrigatórias a Conta de Acesso/Paciente, UUID da operação, impressão HMAC e data. Índice único composto confirmado: conta_acesso_id + operacao_id (88b62714). Schema remoto exportado para o repositório.
- O endpoint versionado consulta a chave composta e reconsulta o comprovante depois da transação/rollback. A consulta prévia de CPF foi retirada para não confundir um reenvio concorrente da mesma operação com duplicação de outra operação. A impressão usa HMAC-SHA256 hexadecimal com chave exclusiva de ambiente.
- Sem CADASTRO_PACIENTE_HMAC_SECRET com pelo menos 32 caracteres, a operação retorna 503 antes de qualquer gravação. A rota de configuração de segredos da Metadata API retornou HTTP 500 com indicação de recurso indisponível no plano gratuito. Nenhum segredo foi criado, impresso ou persistido localmente.
- O usuário informou que configurará a chave depois. A criação completa, o replay, a concorrência e o rollback induzido permanecem pendentes de execução; não publicar o endpoint principal nem habilitar a interface antes dessas verificações.
- tests/test_xano_pacientes_integracao.py compila o endpoint completo em grupo temporário. Os auxiliares de contagem, expiração e falha induzida existem somente nesse grupo. O histórico fica desativado; as contas fictícias são inativadas e o grupo é removido ao finalizar. Testes futuros de sucesso preservarão Pacientes inativados, Prontuários e comprovantes.

### Verificação sem chave — 27/09/2026

- O endpoint de produção e os quatro auxiliares temporários (contagens, falha induzida, falta deliberada da chave e login com validade curta) foram compilados no Xano.
- 7 testes reais passaram em grupo temporário: chave ausente retorna 503 sem registros; array, null e booleano na raiz retornam 400 sem registros; o schema do comprovante exige os quatro campos e índice único composto; UUID com quebra de linha é rejeitado; histórico do grupo permanece vazio.
- A falha do caso de JSON sintaticamente malformado foi removida do conjunto: o parser do gateway Xano devolveu 500 antes de entrar no endpoint. O contrato desta change trata campos ausentes, nulos, de tipo incorreto ou inválidos em corpos JSON; esses cenários continuam cobertos.
- Os testes de sucesso e a sessão expirada foram preparados no grupo, mas aguardam a chave HMAC para concluir os caminhos protegidos e dependentes de autenticação.


### Decisão: impressão SHA-256 sem segredo — 27/09/2026

- O usuário autorizou remover a dependência de `CADASTRO_PACIENTE_HMAC_SECRET`, pois o sistema é somente um projeto acadêmico e a configuração não está disponível no plano gratuito do workspace Xano.
- O endpoint calcula SHA-256 do payload normalizado. Mantêm-se a chave única composta, a transação e a comparação que reconhece reenvio idêntico e rejeita o mesmo UUID com conteúdo diferente. A mudança permanece limitada a dados fictícios.
- A coluna física `impressao_hmac` já criada e vazia é mantida por compatibilidade do schema remoto; seu conteúdo passa a ser o hash SHA-256.
- A integração completa foi liberada para execução sem chave no workspace.
