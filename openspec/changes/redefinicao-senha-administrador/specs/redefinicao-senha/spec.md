## Purpose

Permitir que um Administrador solicite redefinição de senha de uma Conta de Acesso, preservando o controle da nova senha pelo titular e validando toda a operação no Xano.

## ADDED Requirements

### Requirement: Solicitação autorizada e elegibilidade
O sistema SHALL aceitar solicitação apenas de Conta de Acesso ativa com sessão válida e perfil Administrador confirmado no backend. O destinatário SHALL ser uma Conta de Acesso ativa existente, inclusive a própria conta do solicitante; a operação SHALL NOT reativar, desbloquear ou modificar perfis. O destino SHALL ser exclusivamente seu e-mail cadastrado, sem endereço ou retorno arbitrário do cliente.

#### Scenario: Confirmação administrativa
- **WHEN** o Administrador seleciona uma conta ativa e confirma a ação identificada por nome, ID e e-mail mascarado
- **THEN** o backend verifica suas permissões e a conta destinatária antes de reservar o envio
- **AND** a interface não oferece alteração do destinatário nem acesso à senha atual ou definição da nova senha

#### Scenario: Sessão ou perfil insuficiente
- **WHEN** a solicitação ocorre sem sessão válida, com sessão revogada ou após perda do perfil Administrador
- **THEN** o backend rejeita a operação sem envio, inclusive para Recepcionista, Profissional e Paciente sem perfil Administrador

#### Scenario: Conta inelegível
- **WHEN** o Administrador solicita para conta inexistente, inativa ou bloqueada
- **THEN** o backend rejeita a operação sem gerar link utilizável ou alterar a situação da conta

#### Scenario: Própria conta
- **WHEN** o Administrador solicita para a própria Conta de Acesso ativa
- **THEN** são aplicados a mesma confirmação, limites e destino cadastrado, sem tratamento privilegiado

### Requirement: Envio limitado e idempotente
O sistema SHALL limitar solicitações a 10 por hora por Administrador e 3 por hora por Conta de Acesso destinatária, com intervalo mínimo de 60 segundos por destinatário. O replay de operação conhecida do mesmo solicitante/destinatário SHALL NOT produzir novo envio ou consumir cota; reutilização incompatível SHALL ser rejeitada. A garantia de replay e consulta SHALL durar 30 dias desde a reserva no servidor.

#### Scenario: Clique duplo e consulta de resultado
- **WHEN** uma operação conhecida é repetida dentro de 30 dias, inclusive após expiração ou consumo do token
- **THEN** o backend retorna seu resultado atual sem gerar outro token, renovar prazo, consumir nova cota ou reenviar e-mail

#### Scenario: Limite excedido
- **WHEN** uma operação nova excede qualquer limite ou intervalo, inclusive em chamadas concorrentes
- **THEN** o backend rejeita sem envio e informa a espera necessária

### Requirement: Identificador antigo não recria envio
O sistema SHALL reter os metadados mínimos da operação durante a janela garantida e rejeitar a recriação com o mesmo identificador após sua limpeza. A primeira reserva SHALL exigir identificador temporal recente validado pelo servidor; replay conhecido SHALL dispensar esse frescor. Não há promessa de recuperar resultados após 30 dias.

#### Scenario: Identificador desconhecido antigo ou futuro
- **WHEN** a criação apresenta UUIDv7 desconhecido com timestamp anterior a cinco minutos ou mais de 60 segundos no futuro, segundo o Xano
- **THEN** o backend rejeita sem reserva, token, cota ou envio; validade do token nunca é calculada a partir do relógio cliente

#### Scenario: Registro removido depois da janela
- **WHEN** a mesma identificação é apresentada depois dos 30 dias, com ou sem registro físico remanescente
- **THEN** criação retorna409 OPERACAO_ANTIGA e consulta retorna404, sem interpretar a repetição como solicitação nova

### Requirement: Consulta administrativa sem efeitos colaterais
O sistema SHALL separar consulta e criação. O GET de resultado SHALL exigir Administrador ativo, sessão válida e vínculo com solicitante/destinatário originais, sem retornar token ou link. A consulta SHALL NOT criar ou alterar operação, gerar segredo, consumir cota ou enviar e-mail, mesmo para identificação desconhecida. Recepcionista mantém somente a consulta da lista de contas.

#### Scenario: Resultado existente
- **WHEN** o solicitante autorizado consulta sua operação dentro da janela de 30 dias
- **THEN** recebe200 com os estados independentes do envio e do link e suas datas, sem segredos

#### Scenario: Operação não consultável
- **WHEN** o GET apresenta operação desconhecida, de outro vínculo ou fora da janela
- **THEN** retorna404 OPERACAO_NAO_ENCONTRADA e não cria nada nem envia mensagem

#### Scenario: Timeout da criação
- **WHEN** a interface perde a resposta do POST de criação
- **THEN** conserva a identificação e oferece apenas o GET de resultado; erro/404 da consulta não dispara POST ou outra operação automaticamente

### Requirement: Substituição explícita de solicitações
Um reenvio distinto aceito para processamento SHALL invalidar todas as solicitações anteriores imediatamente, mesmo se o novo envio falhar; operação rejeitada antes da reserva SHALL preservar as anteriores.

#### Scenario: Reenvio explícito
- **WHEN** uma nova operação passa pela confirmação, limites e reserva
- **THEN** os links anteriores deixam de funcionar e somente a operação mais recente pode autorizar redefinição

### Requirement: Resultado de envio fiel à evidência
O sistema SHALL distinguir `estado_envio` processando, aceito, falhou e desconhecido, independentemente da validade do link. Nenhum timeout ou erro técnico SHALL provocar repetição automática. A aceitação SHALL NOT ser apresentada como entrega. Sem configuração válida, remetente autorizado, URL pública e proteções de implantação, novos envios SHALL permanecer indisponíveis.

#### Scenario: Provedor aceita
- **WHEN** o provedor aceita explicitamente a mensagem
- **THEN** a interface informa “Solicitação aceita pelo serviço de e-mail; a entrega não foi confirmada”

#### Scenario: Recusa ou resultado incerto
- **WHEN** o provedor recusa, responde de forma incompatível ou não há confirmação por falha de conexão
- **THEN** a interface distingue falha conhecida de resultado incerto, preserva a senha atual e não afirma entrega ou repete o envio automaticamente

### Requirement: Estados terminais do link
O sistema SHALL distinguir `estado_link` pendente, ativo, consumido, expirado, substituido e invalidado. Consumo, substituição e invalidação SHALL preservar o primeiro evento terminal coordenado; sem terminal anterior, expiração no prazo SHALL prevalecer. Resultado tardio do provedor SHALL NOT reativar ou alterar o motivo terminal do link. Link ativo SHALL NOT ser apresentado como entrega ou garantia de elegibilidade da conta.

#### Scenario: Consumo antes de expirar
- **WHEN** um link consumido recebe resposta tardia do provedor ou ultrapassa o prazo
- **THEN** continua consumido, independentemente de o envio ser aceito, falhou ou desconhecido

#### Scenario: Substituição ou expiração antes da resposta
- **WHEN** a resposta do provedor chega após substituição, invalidação ou expiração
- **THEN** somente a dimensão do envio pode ser atualizada; o link não volta a ativo

### Requirement: Confirmação durante envio pendente
O sistema SHALL responder409 ENVIO_EM_PROCESSAMENTO com Retry-After enquanto um token elegível estiver pendente dentro do deadline real do transporte. A operação SHALL NOT consumir o token ou trocar a senha nessa resposta. Depois do deadline sem resultado conclusivo, o envio SHALL ser desconhecido e o link ainda vigente e atual SHALL poder ser confirmado; desconhecimento não significa recusa ou entrega.

#### Scenario: Espera antes do deadline
- **WHEN** o titular confirma durante o processamento de token ainda elegível
- **THEN** a interface informa a espera recebida, limpa senha/confirmação e preserva o código temporário; nova tentativa depende de ação explícita após a espera

#### Scenario: Deadline alcançado sem conclusão
- **WHEN** o prazo máximo realmente imposto à chamada termina sem resposta conclusiva
- **THEN** a confirmação aplica as regras normais de token ativo, sem novo envio, renovação de expiração ou necessidade de aceite do provedor

### Requirement: Token específico de curta duração
O sistema SHALL emitir token imprevisível exclusivo para redefinição, válido por 15 minutos desde sua emissão, armazenando somente uma representação não reversível. O token SHALL estar vinculado à conta, operação e e-mail de destino vigentes; mudança de e-mail, bloqueio ou inativação SHALL impedir seu uso. Ele SHALL NOT autenticar sessão, conceder perfis ou servir a outra operação.

#### Scenario: Validação pública segura
- **WHEN** um código ausente, malformado, inexistente, expirado, substituído ou já usado é apresentado
- **THEN** a redefinição é negada com mensagem genérica, sem revelar conta, e-mail ou estado interno

#### Scenario: Destinatário mudou
- **WHEN** o e-mail da conta mudou ou ela ficou bloqueada/inativa após a emissão
- **THEN** o token anterior não autoriza a troca e a operação não reativa nem desbloqueia a conta

### Requirement: Confirmação atômica e revogação global
O sistema SHALL exigir nova senha de 12 a 128 caracteres, sem remover espaços ou normalizar seu conteúdo, e confirmação correspondente na interface. O backend SHALL aplicar a política e armazenar a senha pelo mecanismo protegido do Xano. Consumo do token, atualização da senha, invalidação de demais solicitações e revogação de todas as sessões da conta SHALL ocorrer atomicamente. Até o commit, a senha atual SHALL permanecer válida. A conclusão SHALL NOT efetuar login automático.

#### Scenario: Sucesso
- **WHEN** o titular confirma uma senha válida com token elegível
- **THEN** exatamente uma troca é concluída, todas as sessões anteriores são revogadas e a pessoa é orientada a entrar novamente

#### Scenario: Concorrência e falha transacional
- **WHEN** duas confirmações usam o mesmo token simultaneamente ou uma etapa da transação falha
- **THEN** no máximo uma confirmação efetiva a troca; uma falha antes do commit não altera parcialmente senha, token ou sessões

#### Scenario: Login concorrente
- **WHEN** um login ocorre simultaneamente à redefinição
- **THEN** uma sessão emitida com a senha antiga não permanece válida após a conclusão

#### Scenario: Senha inválida
- **WHEN** a senha não cumpre a política ou sua confirmação na interface diverge
- **THEN** a operação não troca a senha nem consome o token

### Requirement: Resultado incerto da troca de senha
O sistema SHALL tratar perda de resposta da confirmação como resultado não confirmado, sem afirmar falha ou sucesso e sem repetir automaticamente a troca. A interface SHALL limpar os segredos, encerrar o formulário e orientar tentativa de login com a nova senha. Token já usado SHALL receber a mesma resposta pública genérica dos demais links indisponíveis, sem revelar conta ou estado interno.

#### Scenario: Commit concluído com resposta perdida
- **WHEN** senha e revogações foram efetivadas, mas a resposta204 não chega ao navegador
- **THEN** a interface informa que a senha pode ter sido alterada, oferece login, apaga código/senhas e não executa uma segunda troca

#### Scenario: Reabertura de token usado
- **WHEN** o titular reabre ou confirma um token consumido
- **THEN** recebe400 LINK_INDISPONIVEL sem dados da conta e é orientado a tentar login se já confirmou uma troca ou solicitar outro link

### Requirement: Tela pública e transporte limitado do token
O sistema SHALL disponibilizar formulário de nova senha sem exigir login, mesmo quando já exista sessão na aba, sem expor áreas protegidas. O link SHALL usar exclusivamente URL HTTPS pública fixa configurada no backend, sem localhost para destinatários externos. A abertura ou pré-visualização do link SHALL NOT consumir token, mudar senha ou disparar envio. A exceção de token em URL SHALL depender de aprovação expressa da alteração em acesso-autenticado e das proteções da implantação.

#### Scenario: Entrada pelo link
- **WHEN** o destinatário abre o link com um único código válido em formato
- **THEN** a interface captura o código em estado efêmero isolado, limpa a URL antes de exibir o formulário e valida sua elegibilidade no Xano somente na confirmação

#### Scenario: Entrada inválida ou perda de estado
- **WHEN** há parâmetros duplicados/desconhecidos, falta de código ou recarga após perda do estado efêmero
- **THEN** a interface não tenta recuperar segredo de armazenamento persistente e orienta reabrir o link recebido ou solicitar outro

#### Scenario: Saída da redefinição
- **WHEN** ocorre sucesso, cancelamento, expiração ou retorno ao login
- **THEN** token, senha e confirmação são removidos do estado transitório e nenhuma credencial é colocada na URL de retorno

#### Scenario: Rerun depois da captura
- **WHEN** os campos provocam nova execução depois de limpar a query
- **THEN** o modo público permanece no estado efêmero até sua saída, sem exigir login ou restaurar o segredo na URL

### Requirement: Auditoria e resistência a abuso
O sistema SHALL registrar somente identificadores de solicitante, destinatário e operação, datas e resultado sanitizado, sem senha, token, link completo, e-mail completo ou payload do provedor. A confirmação pública SHALL ter limitação de tentativas independente da autenticação e mensagens sem dados sensíveis. Erros e respostas SHALL impedir cache de conteúdo sensível.

#### Scenario: Abuso da confirmação
- **WHEN** há mais de 30 tentativas de confirmação para a mesma representação não reversível de código em 15 minutos
- **THEN** novas tentativas para esse código são limitadas sem alterar contas ou invalidar tokens de terceiros; proteção de volume no ingresso usa origem confiável, sem confiar em cabeçalho arbitrário do cliente

#### Scenario: Falha com dados sensíveis
- **WHEN** uma dependência devolve detalhes técnicos ou um resultado inesperado
- **THEN** logs, auditoria e interface guardam apenas resultado sanitizado, sem copiar credenciais, corpo de e-mail ou link

### Requirement: Consistência com recuperação já existente
O sistema SHALL impedir que solicitações OTP anteriores ou concorrentes revertam a segurança de uma redefinição concluída por link, e vice-versa. A ativação do novo fluxo SHALL depender de coordenação de consumo/troca entre os mecanismos, preservando os contratos OTP existentes que forem aprovados pelo grupo. Nenhuma alternativa pública SHALL continuar permitindo trocar senha sem revogar sessões e invalidar as demais solicitações da conta.

#### Scenario: Solicitação de outro mecanismo
- **WHEN** uma troca por link ou OTP é concluída enquanto há solicitações de recuperação pendentes em outro mecanismo
- **THEN** as demais solicitações anteriores tornam-se inutilizáveis e a coordenação impede duas trocas concorrentes sobre a mesma geração da credencial

#### Scenario: Dependência não resolvida
- **WHEN** o grupo não aprovou ou não foi comprovada a compatibilidade com o OTP remoto
- **THEN** o fluxo novo permanece desabilitado, sem alterar silenciosamente o comportamento já publicado
