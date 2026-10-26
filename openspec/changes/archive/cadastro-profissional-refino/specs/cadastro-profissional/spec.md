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
