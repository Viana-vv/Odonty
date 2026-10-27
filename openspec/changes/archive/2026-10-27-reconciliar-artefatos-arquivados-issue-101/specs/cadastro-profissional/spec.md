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


## ADDED Requirements

### Requirement: Apresentação responsiva do modal de cadastro de Profissional
O sistema SHALL apresentar o modal administrativo de cadastro de Profissional segundo a hierarquia, espaçamento e agrupamento visual da referência aprovada 10 do kit Sorriso Mais, preservando os campos, contratos e comportamentos existentes.

#### Scenario: Modal em tela ampla
- **WHEN** um Administrador abre o cadastro em uma tela ampla
- **THEN** o título e a descrição ficam separados dos campos, o nome ocupa uma linha inteira, os demais campos são agrupados em colunas legíveis e as ações aparecem no rodapé.

#### Scenario: Modal em tela estreita ou baixa
- **WHEN** um Administrador abre o cadastro em uma janela estreita ou de pouca altura
- **THEN** o modal cabe na área visível, permite rolagem e dispõe campos e ações em uma coluna utilizável.

#### Scenario: Fluxo funcional preservado
- **WHEN** o Administrador preenche ou fecha o modal
- **THEN** continuam disponíveis os campos de nome, especialidade, CRO, e-mail, senha inicial e confirmação, as validações e estados existentes, e as operações permanecem limitadas a `GET /especialidades` e `POST /profissionais` com autorização validada pelo Xano.

