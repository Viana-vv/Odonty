## Why

O catálogo atual de Procedimentos é somente leitura e o atendimento permite apenas marcar um vínculo já criado como realizado. Isso impede que a equipe mantenha o catálogo e que o Profissional ajuste o planejamento durante a Consulta.

## What Changes

- Permitir que Administrador, Recepcionista e Profissional cadastrem Procedimentos no Xano.
- Permitir que Administrador e Recepcionista editem nome, descrição, categoria, duração, valor de referência e situação.
- Permitir que Administrador e Recepcionista inativem um Procedimento sem apagar o histórico.
- Manter a busca e a listagem do catálogo com indicação de situação.
- Permitir que o Profissional visualize os Procedimentos vinculados à Consulta.
- Permitir que o Profissional adicione Procedimentos à Consulta durante o atendimento.
- Permitir marcar um Procedimento como realizado ou cancelado, preservando o vínculo histórico.
- Permitir que a equipe administrativa associe Procedimentos ao agendar uma Consulta.
- Validar todas as operações e permissões no Xano.

## Capabilities

### New Capabilities

- `gestao-procedimentos`: cadastro do catálogo por Administrador, Recepcionista e Profissional; edição, inativação e consulta administrativa por Administrador e Recepcionista.
- `procedimentos-consulta`: planejamento e acompanhamento de Procedimentos vinculados a uma Consulta por Profissional.

### Modified Capabilities

- `catalogo-procedimentos`: ampliar o catálogo existente, atualmente somente leitura, para operações administrativas de manutenção.
- `agenda-consultas`: manter a seleção de Procedimentos no agendamento e permitir que o fluxo use apenas Procedimentos ativos para novas Consultas.

## Impact

- Streamlit: tela do catálogo, tela de Procedimentos da Consulta, formulário de Consulta e navegação por perfil.
- Xano: novos contratos REST para criar/editar/inativar Procedimentos e adicionar/atualizar vínculos de ConsultaProcedimento, com autorização por perfil.
- Cliente Python e testes de contratos Python/JavaScript.
- Documentação do domínio e especificação dos estados históricos.

Fora do escopo: cobrança, pagamento, estoque, cálculo odontológico por dente e exclusão física de Procedimentos ou vínculos.
