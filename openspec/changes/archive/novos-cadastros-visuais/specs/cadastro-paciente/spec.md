## ADDED Requirements

### Requirement: Apresentação visual do cadastro de Paciente
O sistema SHALL apresentar o formulário administrativo de Paciente como um modal seguindo a hierarquia visual, espaçamento, cores e disposição responsiva da referência aprovada `09-novo-paciente.png`, preservando os campos e comportamentos definidos para o cadastro.

#### Scenario: Formulário em tela ampla
- **WHEN** a equipe abre o cadastro de Paciente em uma tela ampla
- **THEN** o modal apresenta título e descrição separados dos campos, prioriza o nome em largura total, agrupa os demais campos relacionados em colunas e mantém as ações no rodapé.

#### Scenario: Formulário em tela estreita
- **WHEN** a equipe abre o cadastro de Paciente em celular ou janela estreita
- **THEN** o modal cabe na área visível, permite rolagem e apresenta os campos e ações em uma coluna legível e utilizável.

#### Scenario: Campos e fluxo preservados
- **WHEN** a equipe usa o formulário atualizado
- **THEN** continuam disponíveis os mesmos campos, rótulos funcionais, validações, mensagens, ações e estados de processamento, sem criar Conta de Acesso ou alterar o contrato do Xano.
