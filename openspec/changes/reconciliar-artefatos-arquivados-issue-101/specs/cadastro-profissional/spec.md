## Purpose

Registrar o requisito corrigido pela retomada local de 02/10/2026, com base na spec arquivada de origem e na tarefa de correção reproduzida em teste.

## MODIFIED Requirements

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
