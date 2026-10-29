## ADDED Requirements

### Requirement: Preservar contexto e privacidade na Nova Evolução
A interface MUST iniciar Nova Evolução com o Paciente filtrado no Prontuário quando ele estiver no escopo das Consultas retornadas. Ao trocar de Paciente, MUST atualizar as Consultas disponíveis e descartar o conteúdo do Paciente anterior. Cancelar, fechar, salvar com sucesso ou encerrar a sessão MUST limpar o rascunho. Falhas recuperáveis MUST preservar o preenchimento sem repetir automaticamente o POST.

#### Scenario: Abrir evolução no Prontuário individual
- **WHEN** o Profissional abre Nova Evolução com um Paciente selecionado e disponível
- **THEN** o formulário inicia com esse Paciente e suas Consultas

#### Scenario: Trocar de Paciente
- **WHEN** o Profissional troca o Paciente no formulário
- **THEN** as opções de Consulta são atualizadas, a Consulta anterior é desmarcada e o texto clínico anterior é removido antes de salvar

#### Scenario: Cancelar ou confirmar a gravação
- **WHEN** o Profissional cancela, fecha ou recebe confirmação da gravação
- **THEN** o formulário fecha e seu rascunho é removido sem alterar os Registros Clínicos existentes

#### Scenario: Falha recuperável durante a gravação
- **WHEN** o Xano rejeita a operação ou a gravação não pode ser confirmada
- **THEN** o formulário preserva o texto, mostra mensagem segura e não repete a chamada automaticamente

#### Scenario: Sessão expirada durante a gravação
- **WHEN** o POST retorna HTTP 401
- **THEN** o sistema remove a sessão e o rascunho e não apresenta o histórico clínico no restante da execução
