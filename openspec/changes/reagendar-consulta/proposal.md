## Why

A equipe administrativa pode agendar e cancelar Consultas, mas ainda não consegue reagendar em uma única operação. A Issue #64 exige preservar a Consulta original e impedir que falhas deixem cancelamento ou reserva parciais.

## What Changes

- Acrescentar operação administrativa de reagendamento com justificativa obrigatória, preservando a Consulta original e criando uma nova Consulta vinculada à Disponibilidade escolhida.
- Persistir vínculo explícito e imutável entre Consulta original e nova, conforme decisão do grupo, em estrutura aditiva com responsável, data e justificativa.
- Validar sessão, autorização, Paciente, Profissional, intervalo e conflitos no Xano; cancelar a original, registrar histórico, liberar o horário anterior e reservar o novo na mesma transação.
- Acrescentar tela Streamlit seguindo a composição aprovada de Nova Consulta do kit Sorriso Mais, com seleção de Paciente, Consulta, Profissional e horário livre.
- Cobrir o novo contrato com testes Python e JavaScript separados por rota e verificar a interface sem rede.
- Corrigir a releitura transacional de Disponibilidade na rota de edição existente, necessária para impedir que uma edição aguardando trava sobrescreva o horário recém-reservado pelo reagendamento.
- Fora do escopo: alterar dados clínicos, migrar registros legados, remover Consultas, editar o modelo de dados sem decisão do grupo ou publicar na API de produção.

## Capabilities

### New Capabilities

- `reagendamento-consulta`: reagendamento administrativo atômico com preservação do histórico e seleção visual de Disponibilidade.

### Modified Capabilities

Nenhuma. O novo fluxo compõe as transições de cancelamento e criação já permitidas.

## Impact

Novo endpoint Xano, tabela aditiva `consulta_reagendamento`, correção delimitada de `PATCH /disponibilidades/{id}` e módulos próprios de integração e interface. A integração de navegação e do cliente comum será realizada pelo agente principal. O grupo autorizou o vínculo persistente explícito entre Consultas e a correção da corrida de Disponibilidade; texto em auditoria não substitui o vínculo. Procedimentos e Registros Clínicos originais permanecem na Consulta antiga e não são copiados. Os testes Xano deverão usar somente grupo temporário, dados fictícios e intervalo mínimo de três segundos entre chamadas.
