## MODIFIED Requirements

### Requirement: Atualização periódica de leituras

As leituras autenticadas SHALL poder ser atualizadas periodicamente na sessão ativa, invalidando o cache privado antes de buscar dados novos. A atualização SHALL preservar o escopo da Conta de Acesso e não SHALL ocorrer durante edição de formulários.

#### Scenario: Outra sessão altera um registro
- **WHEN** uma sessão autenticada permanece aberta e o intervalo periódico é atingido fora de um formulário
- **THEN** o cache privado é invalidado e a tela consulta novamente o Xano

#### Scenario: Formulário em andamento
- **WHEN** a pessoa está preenchendo ou editando um formulário
- **THEN** a atualização periódica não interrompe o fluxo nem descarta os campos

#### Scenario: Sessão expirada
- **WHEN** a atualização periódica detecta sessão expirada ou revogada
- **THEN** o estado autenticado e o cache privado são limpos conforme o fluxo existente
