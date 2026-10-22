## Why

A área Pacientes permanece desabilitada no modo conectado, apesar de existir um contrato autorizado que retorna opções administrativas de Pacientes. A equipe precisa localizar os cadastros ativos sem depender dos dados fictícios da demonstração ou expor dados que a rota não fornece.

## What Changes

- Habilitar uma listagem conectada de Pacientes para Administrador e Recepcionista.
- Apresentar somente identificador e nome retornados por `listar_opcoes_agenda`, com busca por nome e estados de carregamento, erro e lista vazia.
- Reutilizar os padrões visuais do kit Sorriso Mais, adaptando a tabela da referência aos campos efetivamente disponíveis.
- Manter autenticação e autorização na rota existente do Xano.

Fora do escopo: criar ou alterar rotas, cadastrar, editar ou inativar Pacientes, exibir detalhes, CPF, telefone, consultas ou dados clínicos, e usar dados da demonstração no modo conectado.

## Capabilities

### New Capabilities

- `interface-pacientes`: listagem conectada de cadastros ativos com busca nominal e estados de carregamento, erro e vazio.

### Modified Capabilities

Nenhuma.

## Impact

- Streamlit: novo módulo isolado `sorrisomais/pagina_pacientes_xano.py`, integrado à navegação pela coordenação do worktree.
- API: reutiliza exclusivamente `ClienteXano.listar_opcoes_agenda` (GET `/agenda/opcoes`); não altera o cliente nem o contrato Xano.
- Verificação: testes da interface com cliente simulado, sem requisições de rede.
