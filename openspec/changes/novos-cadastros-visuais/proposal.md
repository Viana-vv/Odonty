## Why

Os formulários administrativos de Paciente e Profissional já funcionam, mas a apresentação precisa corresponder melhor às referências aprovadas do kit Sorriso Mais e manter a mesma hierarquia visual nos diferentes tamanhos de tela. A atualização deve facilitar a leitura e o preenchimento sem alterar os dados solicitados nem o fluxo de cadastro.

## What Changes

- Ajustar a composição visual, hierarquia, espaçamento e disposição responsiva dos modais de cadastro de Paciente e Profissional com base nas referências `09-novo-paciente.png` e `10-novo-profissional.png`.
- Preservar todos os campos, rótulos funcionais, validações, mensagens, estados de processamento e ações existentes, além dos contratos e permissões do Xano.
- Não introduzir campos exibidos nas referências que não façam parte dos contratos atuais.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `cadastro-paciente`: especificar o alinhamento visual do modal com a referência do kit, preservando o conjunto de campos e os comportamentos existentes.
- `cadastro-profissional`: especificar o alinhamento visual do cadastro com a referência do kit, preservando o conjunto de campos e os comportamentos existentes.

## Impact

- Interface Streamlit em `sorrisomais/pagina_paciente.py` e `sorrisomais/paginas_equipe.py`.
- Estilos compartilhados em `assets/estilos.css`.
- Specs e testes de interface de cadastro de Paciente e Profissional.
- Nenhuma rota REST, tabela, permissão ou regra de negócio do Xano será alterada.
