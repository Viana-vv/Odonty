## Why

A tela de Agenda conectada ainda está desabilitada, embora os contratos locais de Consultas e Disponibilidades já estejam definidos. A equipe precisa consultar o dia, localizar Consultas e agendar sem depender dos dados fictícios do modo de demonstração.

## What Changes

- Habilitar a área Agenda no modo conectado e apresentar uma lista diária responsiva baseada na referência Sorriso Mais.
- Adicionar busca por Paciente ou Procedimento, data com navegação diária, filtro de situação e ordenação por horário.
- Exibir somente dados administrativos mínimos da Consulta; não exibir telefone nem conteúdo clínico.
- Permitir à Administração e Recepção agendar usando Paciente, Disponibilidade livre, Procedimentos opcionais e múltiplos, e motivo administrativo opcional.
- Permitir alterações de situação somente conforme perfil, transições e autorização já definidas no Xano; solicitar motivo ao cancelar e preservar o histórico.
- Completar contratos REST de leitura para a tela, retornando rótulos administrativos necessários e fornecendo opções ativas de Paciente, Profissional e Procedimento com escopo autorizado.
- Reconciliar schemas existentes de Disponibilidade, Consulta e vínculos no workspace Xano; criar ou publicar somente estruturas ausentes, sem remover ou reescrever dados históricos.

Fora do escopo: calendário semanal/mensal, gestão visual de horários disponíveis/bloqueados, exibição de telefone ou informação clínica, edição/exclusão de Consulta, e publicação de mudanças sem revisão final.

## Capabilities

### New Capabilities

- `agenda-consultas`: dados administrativos de leitura necessários à grade diária e às opções de agendamento, mantendo autorização e histórico no Xano.
- `interface-agenda`: navegação, filtros, lista diária, estados vazios/erro e fluxo de agendamento conectado.

### Modified Capabilities

Nenhuma. As capacidades correspondentes ainda não existem em `openspec/specs/`.

## Impact

- Streamlit: `sorrisomais/paginas_equipe.py`, cliente REST em `sorrisomais/api.py`, validações em `sorrisomais/contratos_clinicos.py`, navegação e estilos.
- Xano: consultas GET e POST existentes, consulta de Disponibilidades, possíveis rotas GET de opções administrativas e tabelas relacionais já descritas em `backend/xano`.
- Verificação: contratos Python e JavaScript por rota, testes de interface com clientes HTTP simulados e inspeção da versão renderizada com dados fictícios.
- A integração conectada foi publicada. Em 07/10/2026, a conferência em execução encontrou erros nas rotas de Agenda; as validações e a serialização de datas foram corrigidas. GET `/disponibilidades` e GET `/consultas` respondem 200; uma Disponibilidade fictícia foi criada para 08/10/2026, às 09h. A conferência visual dos três perfis segue pendente.

- O smoke test real de POST /consultas encontrou HTTP 500 por uma expressao incompatível com o Xano. A rota foi corrigida e publicada; o POST real retornou HTTP 201 usando dados fictícios. Para teste pela interface, há uma Consulta às 09h e uma Disponibilidade livre às 10h em 08/10/2026.

- Uma nova falha ao repetir o agendamento levou a remover o pipe default dos contadores de concorrência existentes no POST. A versão atual foi publicada no Xano; o horário das 10h permanece livre para novo teste.
