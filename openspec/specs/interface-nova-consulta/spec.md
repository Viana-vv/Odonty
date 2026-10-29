# interface-nova-consulta Specification

## Purpose
Restaurar na especificação vigente os requisitos aprovados nos deltas arquivados para a capacidade `interface-nova-consulta`.

## Requirements

### Requirement: Agendamento em tela própria
A interface MUST apresentar Nova Consulta em uma tela própria seguindo a hierarquia e os controles da referência visual aprovada. Somente Administrador e Recepcionista podem receber o formulário. Deve permitir escolher Paciente ativo, Profissional ativo, data da Consulta, Disponibilidade livre correspondente ao Profissional e à data, zero ou mais Procedimentos ativos e observação administrativa opcional.

#### Scenario: Carregar formulário autorizado
- **WHEN** Administrador ou Recepcionista abre Nova Consulta
- **THEN** a interface carrega opções ativas pelo contrato existente e permite preencher os dados da Consulta

#### Scenario: Data e horário dependentes
- **WHEN** a equipe seleciona Profissional e data da Consulta
- **THEN** a interface consulta as Disponibilidades desse Profissional para o intervalo daquela data e apresenta seus horários

#### Scenario: Atualizar opções e horários
- **WHEN** a equipe solicita a atualização dos dados da tela
- **THEN** a interface refaz as leituras de opções e Disponibilidades usando os contratos existentes

#### Scenario: Envio válido
- **WHEN** a equipe envia Paciente, Disponibilidade e campos opcionais válidos
- **THEN** a interface envia uma Consulta pelo contrato POST existente e confirma sucesso somente após resposta positiva do Xano

#### Scenario: Campo obrigatório ausente
- **WHEN** Paciente ou Disponibilidade não foi selecionado
- **THEN** a interface mantém a tela aberta, informa o campo pendente e não envia a requisição

#### Scenario: Conflito ou falha de API
- **WHEN** o Xano rejeita a criação por conflito, autorização, validação ou indisponibilidade
- **THEN** a interface mostra mensagem compreensível, preserva os dados preenchidos e permite corrigir ou tentar novamente

#### Scenario: Perfil sem permissão
- **WHEN** um Profissional ou Paciente tenta renderizar o formulário
- **THEN** a interface não apresenta controles para criar Consulta

### Requirement: Proteção e minimização de dados
A interface MUST reutilizar os contratos REST existentes e MUST NOT presumir endpoints novos. A validação de autorização, disponibilidade e conflitos permanece no Xano. A tela MUST NOT mostrar dados além dos nomes e identificadores necessários ao agendamento, nem registrar tokens ou dados clínicos.

#### Scenario: Opções ou Disponibilidades indisponíveis
- **WHEN** uma leitura falha ou a sessão expira
- **THEN** a interface apresenta erro seguro, não exibe opções desatualizadas como atuais e não envia a criação
