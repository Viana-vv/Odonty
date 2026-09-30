## Purpose

Permitir que a equipe administrativa cadastre Pacientes com dados fictícios e crie seus Prontuários de forma vinculada, sem conceder acesso clínico ou criar credenciais de login.

## ADDED Requirements

### Requirement: Cadastro autorizado pela equipe
O sistema SHALL permitir cadastrar Paciente somente a Administrador ou Recepcionista ativos com sessão válida. A autorização SHALL ser verificada no backend em cada envio, independentemente da navegação e dos perfis apresentados pela interface.

#### Scenario: Equipe autorizada
- **WHEN** um Administrador ou Recepcionista ativo envia dados válidos com sessão válida
- **THEN** o sistema permite a criação do Paciente e preserva a identidade da pessoa que cadastrou.

#### Scenario: Perfil não autorizado
- **WHEN** uma conta apenas de Profissional ou Paciente tenta cadastrar diretamente pela API
- **THEN** a operação é negada sem criação de registros.

#### Scenario: Perda de acesso
- **WHEN** a sessão está ausente, expirada ou revogada, ou a conta está inativa, bloqueada ou perdeu os perfis autorizados
- **THEN** o backend rejeita o cadastro e a interface interrompe o acesso ao formulário, limpando seus dados.

### Requirement: Dados cadastrais do Paciente
O sistema SHALL exigir os seis campos cadastrais: nome completo de 2 a 120 caracteres, data de nascimento válida não futura, telefone, CPF, e-mail e celular. Telefone e celular devem conter 10 ou 11 dígitos ASCII depois de normalizar espaços, parênteses e hífen; CPF deve passar pela validação dos dígitos verificadores; e-mail deve ter formato válido e até 254 caracteres. O cadastro SHALL utilizar somente dados fictícios e SHALL NOT pedir senha, perfil ou conteúdo clínico.

#### Scenario: Cadastro mínimo
- **WHEN** a equipe informa nome, nascimento e todos os contatos válidos
- **THEN** o sistema aceita o cadastro e normaliza os contatos antes de persistir.

#### Scenario: Dados inválidos
- **WHEN** o nome está vazio ou fora do limite, o nascimento é inválido ou futuro, o telefone está ausente, nulo, vazio ou inválido, ou telefone, CPF, e-mail ou celular está ausente ou inválido
- **THEN** o cadastro é rejeitado com orientação compreensível, sem criação parcial.

#### Scenario: Todos os campos validados no backend
- **WHEN** uma chamada direta omite qualquer campo obrigatório ou envia null, texto vazio, somente espaços, tipo diferente de string ou valor fora do formato
- **THEN** o backend rejeita o cadastro com 400 sem criar Paciente, Prontuário ou comprovante de operação.

#### Scenario: Campos adulterados
- **WHEN** o envio contém campos extras como situação, perfil, conta vinculada ou informações clínicas
- **THEN** o backend rejeita o cadastro sem aplicar os valores recebidos.

### Requirement: CPF obrigatório e único
O sistema SHALL exigir CPF não vazio, válido e impedir sua duplicação, inclusive entre pacientes inativos e em envios simultâneos. SHALL NOT usar nome, nascimento ou contato como chave única.

#### Scenario: Duplicação concorrente
- **WHEN** dois envios distintos utilizam o mesmo CPF normalizado
- **THEN** no máximo um Paciente é criado e o outro envio recebe mensagem de duplicação sem revelar o cadastro existente.

#### Scenario: Contatos compartilhados
- **WHEN** pessoas diferentes compartilham telefone, e-mail ou celular
- **THEN** o compartilhamento não impede seu cadastro.

### Requirement: Paciente e Prontuário criados conjuntamente
O sistema SHALL criar um Paciente ativo e exatamente um Prontuário vazio vinculado na mesma operação atômica, com identificadores e datas gerados no backend. O sistema SHALL NOT criar Conta de Acesso, Registro Clínico, Consulta ou credencial de Paciente nessa operação, nem permitir acesso ao conteúdo clínico pela equipe administrativa.

#### Scenario: Criação integral
- **WHEN** o cadastro é concluído
- **THEN** existem um Paciente e seu único Prontuário, sem conta ou registro clínico criado.

#### Scenario: Falha de gravação
- **WHEN** ocorre falha ao gravar qualquer parte da operação
- **THEN** nenhum Paciente ou Prontuário parcial permanece.

### Requirement: Reenvio seguro após resultado incerto
O sistema SHALL impedir envios simultâneos pela interface, não repetir automaticamente a criação e reconhecer reenvios da mesma operação sem duplicar Paciente ou Prontuário. A chave da operação SHALL ser vinculada à Conta de Acesso solicitante; sua reutilização com dados diferentes SHALL ser rejeitada.

#### Scenario: Resposta perdida
- **WHEN** a criação foi confirmada no backend, mas a resposta se perde e a mesma operação é reenviada manualmente
- **THEN** o backend retorna o resultado já criado sem gravar outro Paciente ou Prontuário.

#### Scenario: Operação reutilizada com alterações
- **WHEN** uma chave de operação já concluída é enviada com dados diferentes
- **THEN** o backend informa conflito sem criar ou alterar registros.

#### Scenario: Falha sem confirmação
- **WHEN** ocorre timeout, falha de rede ou resposta incompatível
- **THEN** a interface informa que o resultado não foi confirmado, preserva a operação para uma tentativa manual e não apresenta sucesso.

### Requirement: Formulário utilizável e dados protegidos
O sistema SHALL oferecer Cadastrar e Voltar, manter o formulário utilizável em computador, tablet, celular e teclado, limpar dados após sucesso, saída, logout ou perda de acesso e preservar os campos após erro corrigível. Dados pessoais SHALL NOT aparecer em URLs, logs, cache compartilhado ou mensagens técnicas.

#### Scenario: Sucesso e novo cadastro
- **WHEN** o backend confirma a criação
- **THEN** a interface mostra confirmação, limpa os campos e prepara uma nova operação.

#### Scenario: Erro corrigível
- **WHEN** o backend rejeita dados inválidos ou CPF duplicado
- **THEN** a interface preserva os dados para correção e reabilita o envio.

#### Scenario: Navegação e privacidade
- **WHEN** a pessoa volta à página inicial, sai ou perde a sessão
- **THEN** os dados do formulário são removidos do estado da interface.

#### Scenario: Dispositivos e teclado
- **WHEN** a equipe utiliza computador, tablet, celular ou navegação por teclado
- **THEN** os campos e ações permanecem legíveis, alcançáveis e com foco visível.
