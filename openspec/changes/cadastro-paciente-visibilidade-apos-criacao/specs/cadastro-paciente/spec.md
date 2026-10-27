# cadastro-paciente Specification

## ADDED Requirements

### Requirement: Rota do formulário permanece disponível durante o envio
O sistema SHALL manter a rota administrativa de cadastro de Paciente durante cada rerun do formulário, até que a operação seja concluída, rejeitada ou abandonada pela equipe.

#### Scenario: Envio pelo modal
- **WHEN** Administrador ou Recepcionista abre o cadastro e envia dados válidos
- **THEN** o formulário continua montado durante o processamento e o cliente REST recebe um único POST.

#### Scenario: Resultado incerto
- **WHEN** o POST termina sem confirmação
- **THEN** o formulário permanece acessível com a operação e os dados pendentes para reenvio manual.

### Requirement: Atualização da listagem após cadastro confirmado
Após o Xano confirmar e o cliente validar a resposta de criação, o sistema SHALL invalidar o cache da lista de Pacientes da sessão antes de retornar à listagem.

#### Scenario: Cadastro confirmado
- **WHEN** o POST `/pacientes` retorna sucesso compatível
- **THEN** o cache de Pacientes é invalidado e a listagem busca dados atualizados na próxima renderização.

#### Scenario: Resultado não confirmado
- **WHEN** ocorre timeout, falha de rede ou resposta incompatível
- **THEN** o cache não é tratado como confirmação, a operação pendente e sua chave idempotente permanecem disponíveis para reenvio manual, e nenhum sucesso é apresentado.

#### Scenario: Rejeição do cadastro
- **WHEN** o Xano rejeita os dados ou informa CPF duplicado
- **THEN** a lista não é invalidada por sucesso inexistente e o formulário preserva os dados necessários para correção.

