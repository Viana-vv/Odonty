## ADDED Requirements

### Requirement: Apresentação visual do cadastro de Profissional
O sistema SHALL apresentar o formulário administrativo de Profissional seguindo a hierarquia visual, espaçamento, cores e disposição responsiva da referência aprovada `10-novo-profissional.png`, preservando os campos e comportamentos definidos para a criação vinculada de Profissional e Conta de Acesso.

#### Scenario: Formulário em tela ampla
- **WHEN** um Administrador abre o cadastro de Profissional em uma tela ampla
- **THEN** o modal apresenta título e descrição separados dos campos, prioriza o nome em largura total, organiza campos relacionados em colunas e mantém as ações no rodapé.

#### Scenario: Formulário em tela estreita
- **WHEN** um Administrador abre o cadastro de Profissional em celular ou janela estreita
- **THEN** o modal cabe na área visível, permite rolagem e apresenta os campos e ações em uma coluna legível e utilizável.

#### Scenario: Campos, permissões e fluxo preservados
- **WHEN** um Administrador usa o formulário atualizado
- **THEN** continuam disponíveis os mesmos campos, rótulos funcionais, validações, mensagens, ações e estados de processamento, e a autorização e criação vinculada continuam validadas pelo Xano.
