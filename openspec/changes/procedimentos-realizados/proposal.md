## Why

A Consulta pode conter vários procedimentos planejados, mas a equipe Profissional ainda não consegue registrar quais foram realizados. A conclusão precisa preservar os dados de planejamento e identificar separadamente o Profissional e a data de realização.

## What Changes

- Acrescentar situação `planejado` e campos próprios de realização em `ConsultaProcedimento`, sem reinterpretar os dados existentes de planejamento.
- Disponibilizar consulta de procedimentos vinculados e uma transição autenticada de `planejado` para `realizado`, limitada ao Profissional responsável pela Consulta.
- Apresentar, em tela Streamlit no padrão Sorriso Mais, procedimentos da Consulta e o controle para marcar como realizado.
- Criar testes unitários isolados por rota REST para Python e JavaScript e testes de interface.

Fora do escopo: desfazer ou editar realizações, alterar pagamentos, mudar a Consulta, migrar registros históricos, integração da navegação principal e validação em grupo Xano de produção.

## Capabilities

### New Capabilities

- `procedimentos-consulta-realizados`: consultar e marcar como realizados os procedimentos planejados de uma Consulta, preservando autoria e data do planejamento.

### Modified Capabilities

Nenhuma.

## Impact

- Export de tabela e APIs Xano em `backend/xano`.
- Módulo dedicado de cliente REST e tela Streamlit em novos arquivos `sorrisomais`.
- Testes Python e JavaScript por rota e testes da tela.
- A validação de alterações do Xano deve ocorrer somente em grupo temporário; a migração requer que vínculos existentes recebam situação `planejado` sem sobrescrever campos atuais.
