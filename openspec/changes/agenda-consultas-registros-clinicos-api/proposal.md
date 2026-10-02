## Why

O workspace Xano ainda não oferece os contratos necessários para disponibilidades da Agenda nem para Registros Clínicos separados do Prontuário. A tabela legada `consulta` não referencia uma disponibilidade e aceita apenas um Procedimento, o que impede cumprir as cardinalidades e os controles de conflito definidos no modelo de domínio.

## What Changes

- Especificar APIs REST para consultar e administrar disponibilidades da Agenda e para criar, consultar e atualizar a situação das Consultas, com validação e autorização no Xano.
- Definir listagens de Consultas com escopo por perfil e sem exposição de informações clínicas em listagens administrativas.
- Especificar Registros Clínicos relacionados ao Prontuário, Paciente, Profissional e, quando aplicável, à Consulta, preservando o histórico e restringindo acesso por perfil.
- Definir uma estratégia não destrutiva para compatibilidade das estruturas legadas `consulta` e `prontuario`; nenhuma migração de registros existentes será feita sem revisão do contrato e da estratégia.
- Manter fora desta change as telas Streamlit, APIs de Exame, implantação e migração de dados existentes.

## Capabilities

### New Capabilities

- `agenda-consultas`: disponibilidades, agendamento, consulta e atualização de situação, conflitos de horário, listagens e permissões.
- `registro-clinico`: criação e consulta de Registros Clínicos com vínculos e permissões coerentes com o modelo de domínio.

### Modified Capabilities

Nenhuma. As capacidades de Agenda/Consultas e Registro Clínico ainda não possuem specs principais neste repositório.

## Impact

Afeta contratos REST e schemas no Xano, cliente Python e testes unitários por rota que forem necessários na etapa de implementação. A inspeção read-only do workspace 149129 encontrou a tabela `consulta` sem vínculo com Disponibilidade e com apenas um `procedimento_id`; não encontrou schemas de Agenda/Disponibilidade, Registro Clínico ou Exame, nem endpoints do grupo Sorriso Acesso para essas operações. Os contratos e a compatibilidade legada precisam de revisão antes de qualquer publicação.
