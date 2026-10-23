## Motiva??o

Profissionais precisam registrar uma evolução durante o atendimento sem sair do histórico clínico do Paciente. A tela deve oferecer um fluxo claro e manter a criação vinculada ao Prontuário e à Conta de Acesso profissional autenticada.

## O que muda

- Adicionar ao histórico clínico uma tela para registrar um novo Registro Clínico no Prontuário de um Paciente.
- Usar as Consultas retornadas no escopo do Profissional para selecionar Paciente e, opcionalmente, vincular uma Consulta.
- Reutilizar o contrato Xano existente `POST /registros-clinicos`; o Xano identifica o Profissional autenticado, valida seu acesso, localiza o Prontuário ativo e preserva o histórico.
- Adaptar a referência visual aprovada para os campos suportados pelo contrato existente.
- Registrar que o contrato não aceita data informada, Profissional selecionável ou Procedimento; esses dados não serão apresentados como graváveis nesta mudança.

## Capacidades

### Novas capacidades
- `registro-evolucao-clinica`: criar Registro Clínico de um Paciente a partir de uma Conta de Acesso de Profissional autorizada, preservando o histórico.

### Capacidades modificadas

## Impacto

- Streamlit: nova tela e navegação no espaço de Prontuários.
- Xano/API: reutilização de `GET /consultas`, `GET /registros-clinicos` e `POST /registros-clinicos`, sem alteração de contrato.
- Testes: UI isolada sem rede e testes Python e JavaScript separados por rota para os contratos REST usados.
- GitHub Issue vinculada à tarefa, se a integração GitHub estiver disponível.
