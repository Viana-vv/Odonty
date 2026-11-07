## MODIFIED Requirements

### Requirement: Tela informativa e somente leitura
A tela MUST exibir as Contas de Acesso autorizadas sem oferecer controles para editar perfis ou situação, definir senhas ou criar contas. A única ação de credenciais permitida SHALL ser “Enviar link de redefinição de senha”, exclusiva de Administrador, com confirmação e conforme redefinicao-senha; Recepcionista SHALL manter somente consulta. A solicitação SHALL NOT expor ou permitir escolher a senha do titular.

#### Scenario: Cenário: Lista vazia
- **WHEN** a consulta autorizada não encontra Contas de Acesso
- **THEN** a tela informa que não há Contas de Acesso para exibir

#### Scenario: Cenário: Falha de consulta
- **WHEN** a API falha
- **THEN** a tela mostra uma mensagem compreensível sem detalhes técnicos ou dados sensíveis

#### Scenario: Ação exclusiva
- **WHEN** a conta autenticada possui perfil Administrador e a configuração local de novos envios está habilitada
- **THEN** a tela permite solicitar o link mediante confirmação com nome, ID e e-mail mascarado, sem campo de destinatário editável
- **AND** o backend continua verificando autorização, disponibilidade remota e dependências antes da reserva

#### Scenario: Consulta sem permissão de envio
- **WHEN** uma conta somente Recepcionista acessa a tela
- **THEN** visualiza a lista e sua atualização, sem controle de envio; chamadas diretas de envio continuam sendo negadas no Xano

## ADDED Requirements

### Requirement: Acesso à listagem pelo menu autorizado
O sistema SHALL tornar a listagem existente de Contas de Acesso alcançável pela navegação autenticada de Administrador e Recepcionista, respeitando os contratos atuais de consulta. Os demais perfis SHALL NOT obter acesso por mudança local de rota.

#### Scenario: Navegação permitida
- **WHEN** Administrador ou Recepcionista abre Contas de Acesso pelo menu
- **THEN** a aplicação reutiliza a listagem existente e suas mensagens de carregamento, erro e lista vazia

#### Scenario: Navegação indevida
- **WHEN** perfil sem permissão tenta acessar diretamente essa área
- **THEN** a aplicação não exibe contas e o backend rejeita consulta ou envio sem autorização

### Requirement: Disponibilidade de novos envios separada de autorização
O Streamlit SHALL ler a flag pública de novos envios do ambiente, desligada por padrão, sem tratá-la como autorização. Ausência, erro ou valor inválido SHALL impedir somente novos envios; login, menu, lista e atualização permanecem. A flag remota do Xano e a validação de Administrador SHALL continuar definitivas para primeira reserva.

#### Scenario: Carregamento e erro local
- **WHEN** a configuração local ainda não foi lida ou é inválida
- **THEN** nenhum envio fica habilitado; erro gera aviso compreensível ao Administrador sem derrubar o cliente de API ou ocultar a consulta de contas

#### Scenario: Indisponibilidade normal
- **WHEN** a flag local está ausente ou desligada
- **THEN** a interface não oferece novos envios e preserva lista/atualização para Administrador e Recepcionista

#### Scenario: Configurações divergentes
- **WHEN** a flag local permite o botão, mas o Xano não permite novos envios
- **THEN** o POST retorna503 RECURSO_INDISPONIVEL sem reserva, token ou envio e a interface informa indisponibilidade sem alegar falha da lista

### Requirement: Consulta de resultado e desligamento de envios
O sistema SHALL permitir ao Administrador consultar sua operação por GET, separadamente do botão de envio, mesmo com novos envios desligados. O desligamento normal SHALL NOT invalidar links vigentes; revogação emergencial explícita SHALL torná-los indisponíveis sem reativação. Recepcionista SHALL NOT obter acesso às operações de redefinição.

#### Scenario: Atualização do resultado
- **WHEN** o Administrador pede consulta de sua operação
- **THEN** a interface apresenta carregamento e depois os estados separados de envio/link; erro ou404 informa resultado não disponível sem disparar criação ou novo identificador

#### Scenario: Flag desligada após emissão
- **WHEN** novos envios são desligados depois da reserva de uma operação
- **THEN** a consulta autorizada e a confirmação pública de link ainda elegível permanecem disponíveis, sem novos envios
