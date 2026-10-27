## ADDED Requirements
### Requirement: Cache sob demanda de leituras GET privadas
O sistema SHALL reutilizar respostas GET bem-sucedidas durante a sessão Streamlit por escopo da Conta de Acesso e parâmetros da leitura, sem pré-carregar dados e sem compartilhar respostas privadas entre sessões/identidades. A chave SHALL usar hash unidirecional e SHALL nunca conter token bruto. Cache SHALL residir apenas no estado da sessão.

#### Scenario: Primeira abertura e retorno à página
- **WHEN** a Conta de Acesso abre uma página ainda não carregada
- **THEN** a UI executa o GET solicitado e guarda a resposta válida; ao navegar e voltar, reutiliza a resposta sem rede

#### Scenario: Atualização ou mutação bem-sucedida
- **WHEN** a pessoa solicita atualização manual ou conclui uma mutação que afeta a leitura
- **THEN** a leitura afetada é executada novamente e dependências documentadas são invalidadas

#### Scenario: Falha de rede ou resposta inválida
- **WHEN** o loader falha ou a resposta GET não é válida
- **THEN** a falha não é armazenada nem substituída por dados de uma identidade anterior

#### Scenario: Acesso recusado ou sessão encerrada
- **WHEN** o Xano retorna 401/403 ou ocorre logout, expiração ou troca de Conta de Acesso/perfil
- **THEN** os dados privados em cache são apagados antes de continuar

#### Scenario: Dados clínicos ou pessoais
- **WHEN** uma resposta contém dados pessoais/clínicos
- **THEN** ela permanece somente em `session_state`, sem cache global compartilhado ou logs
