## MODIFIED Requirements

### Requirement: Criar Registro Clínico vinculado
O sistema MUST permitir que Profissional ativo e autorizado crie Registro Clínico associado ao Prontuário do Paciente e, quando informado, à Consulta correspondente. O Registro poderá manter conteúdo legado textual ou campos estruturados de Evolução Clínica, mas o Paciente, Profissional, Prontuário e Consulta relacionados MUST ser compatíveis.

#### Scenario: Criar registro para atendimento próprio
- **WHEN** Profissional autorizado registra informações de uma Consulta que pertence ao Paciente e ao próprio Profissional
- **THEN** o sistema cria uma Evolução Clínica com autoria e data identificadas no Prontuário correto

#### Scenario: Rejeitar vínculos inconsistentes
- **WHEN** o Registro Clínico referencia Consulta, Paciente ou Prontuário incompatíveis
- **THEN** o sistema rejeita a operação sem gravar registro parcial

#### Scenario: Impedir criação por perfil administrativo
- **WHEN** Administrador ou Recepcionista tenta criar Registro Clínico sem perfil profissional autorizado
- **THEN** o sistema retorna acesso negado sem alterar o histórico clínico
