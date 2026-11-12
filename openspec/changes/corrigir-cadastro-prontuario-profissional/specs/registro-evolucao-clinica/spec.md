# Registro de evolução clínica — correção de vínculo

## MODIFIED Requirements

### Requirement: usar a Consulta validada no Registro Clínico

O Xano MUST gravar o `consulta_id` da Consulta explicitamente validada ou da
Consulta encontrada no escopo do Profissional quando o formulário não informar
uma Consulta.

#### Cenário: salvar sem Consulta explícita

- **DADO** um Profissional ativo autorizado e um Paciente ativo com Prontuário
  ativo e Consulta no escopo do Profissional
- **QUANDO** o Profissional salva uma evolução sem `consulta_id`
- **ENTÃO** o Xano cria o Registro Clínico vinculado ao Prontuário e à Consulta
  validada, sem ampliar o escopo de acesso

#### Cenário: salvar com Consulta explícita

- **DADO** uma Consulta pertencente ao Paciente e ao Profissional autenticado
- **QUANDO** o Profissional salva uma evolução informando o `consulta_id`
- **ENTÃO** o Xano cria o Registro Clínico usando essa Consulta após validar os
  vínculos

#### Cenário: vínculo não encontrado

- **QUANDO** Paciente, Prontuário ou Consulta não estiver no escopo permitido
- **ENTÃO** o Xano rejeita a operação sem criar Registro Clínico

