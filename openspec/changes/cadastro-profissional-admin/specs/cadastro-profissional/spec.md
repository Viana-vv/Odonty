## Purpose

Permitir que um Administrador cadastre um Profissional e sua Conta de Acesso de forma vinculada, para uso do login da equipe separado do acesso de pacientes.

## ADDED Requirements

### Requirement: Cadastro exclusivo de Administrador
O sistema SHALL permitir cadastrar Profissional somente a uma Conta de Acesso ativa com perfil administrador e sessão válida, com autorização no backend em cada envio.

#### Scenario: Administrador autorizado
- **WHEN** um Administrador ativo com sessão válida envia um cadastro válido
- **THEN** o sistema permite a criação vinculada.

#### Scenario: Perfil sem permissão
- **WHEN** um Profissional, Recepcionista ou Paciente chama diretamente a operação de cadastro
- **THEN** o backend nega o acesso e não cria registros.

#### Scenario: Sessão inválida ou permissão perdida
- **WHEN** o solicitante está sem autenticação, com sessão expirada ou revogada, conta bloqueada/inativa ou perdeu o perfil administrador
- **THEN** o cadastro é rejeitado e a interface interrompe o acesso administrativo.

### Requirement: Formulário da equipe separado de pacientes
O sistema SHALL apresentar Cadastrar profissional em página administrativa protegida, separada do cadastro e login de Paciente. O cadastro SHALL exigir nome, e-mail, senha inicial, CRO e seleção de especialidade ativa existente. A interface SHALL pedir confirmação da senha e identificar o perfil fixo como Dentista.

#### Scenario: Abrir cadastro
- **WHEN** o Administrador seleciona Cadastrar profissional
- **THEN** visualiza o formulário com rótulos em português, senha mascarada, perfil Dentista e ações Cadastrar e Voltar.

#### Scenario: Campos inválidos
- **WHEN** há campo obrigatório vazio, e-mail inválido, senha fora dos limites definidos, confirmação divergente ou CRO inválido
- **THEN** o sistema orienta a correção e não conclui cadastro; o backend valida os campos recebidos independentemente da interface.

#### Scenario: Acesso por teclado ou celular
- **WHEN** o formulário é utilizado em computador, tablet, celular ou por teclado
- **THEN** os controles permanecem legíveis, alcançáveis e com foco visível.

### Requirement: Criação vinculada sem duplicação
O sistema SHALL criar conjuntamente um Profissional ativo e uma Conta de Acesso ativa com exclusivamente o perfil profissional. O e-mail normalizado da conta e o CRO normalizado SHALL ser únicos, inclusive em envios concorrentes. A operação SHALL concluir integralmente ou não criar nenhum dos dois registros.

#### Scenario: Cadastro concluído
- **WHEN** dados válidos e inéditos são enviados por Administrador autorizado
- **THEN** um Profissional e uma Conta de Acesso são criados e vinculados, e o sucesso é confirmado sem devolver senha ou token.

#### Scenario: E-mail ou CRO duplicado
- **WHEN** o e-mail ou CRO informado já existe, inclusive em registro inativo ou em envio concorrente
- **THEN** o cadastro é recusado com mensagem compreensível e sem registro parcial.

#### Scenario: Falha durante a criação
- **WHEN** a gravação de qualquer parte da criação vinculada falha
- **THEN** nenhuma nova conta ou profissional parcial permanece.

#### Scenario: Tentativa de escolher privilégio
- **WHEN** o envio inclui perfil, situação, identificador de conta ou outros campos não aceitos
- **THEN** o backend rejeita o envio sem criar conta administrativa ou alterar registros existentes.

### Requirement: Login do Profissional criado
O sistema SHALL permitir que o Profissional cadastrado entre pelo login da equipe com e-mail e senha inicial, usando as regras existentes de autenticação, expiração e logout.

#### Scenario: Primeira entrada
- **WHEN** o Dentista recém-cadastrado envia suas credenciais corretas
- **THEN** recebe acesso à sua identificação e saída, sem ações administrativas.

#### Scenario: Sessão do Administrador preservada
- **WHEN** o Administrador conclui o cadastro
- **THEN** continua identificado como Administrador e não assume a identidade da conta criada.

### Requirement: Tratamento de envio e proteção da senha
O sistema SHALL impedir submissões simultâneas pela interface, remover senha e confirmação após processamento ou saída da página, não registrar credenciais e não repetir automaticamente cadastros. Falhas de resultado incerto SHALL NOT ser apresentadas como sucesso.

#### Scenario: Sucesso na interface
- **WHEN** o backend confirma a criação
- **THEN** a interface informa sucesso, limpa os campos e permite outro cadastro.

#### Scenario: Falha de conexão ou resposta inválida
- **WHEN** a resposta é perdida, vazia ou incompatível
- **THEN** a interface informa que não confirmou o cadastro, remove as senhas e reabilita o formulário sem repetir a requisição.

#### Scenario: Duplo clique
- **WHEN** a pessoa aciona Cadastrar novamente durante o processamento
- **THEN** a interface mantém apenas um envio em andamento.

#### Scenario: Logs e erros
- **WHEN** ocorre sucesso ou erro durante o cadastro
- **THEN** senha, token e corpos sensíveis não aparecem em logs, respostas ou mensagens técnicas.

### Requirement: Seleção de especialidade existente
O sistema SHALL oferecer somente especialidades ativas para seleção, com consulta autorizada exclusivamente para Administrador. O backend SHALL validar existência e situação da especialidade em cada cadastro.

#### Scenario: Especialidade inexistente ou inativa
- **WHEN** o envio referencia especialidade removida, inexistente ou inativa
- **THEN** o cadastro é rejeitado sem criar registros.

#### Scenario: Nenhuma especialidade disponível
- **WHEN** a lista autorizada de especialidades está vazia
- **THEN** o formulário impede envio e orienta configurar especialidades no Xano.

#### Scenario: Consulta sem autorização
- **WHEN** uma conta sem perfil administrador consulta especialidades por essa operação
- **THEN** o backend nega o acesso.
