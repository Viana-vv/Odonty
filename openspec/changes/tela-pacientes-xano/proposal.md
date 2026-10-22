## Why

A área Pacientes permanece desabilitada no modo conectado, apesar de existir um contrato autorizado que retorna opções administrativas de Pacientes. A equipe precisa localizar os cadastros ativos sem depender dos dados fictícios da demonstração ou expor dados que a rota não fornece.

## What Changes

- Habilitar uma listagem conectada de Pacientes para Administrador e Recepcionista.
- Apresentar somente identificador e nome retornados por `listar_opcoes_agenda`, com busca por nome e estados de carregamento, erro e lista vazia.
- Reutilizar os padrões visuais do kit Sorriso Mais, adaptando a tabela da referência aos campos efetivamente disponíveis.
- Manter autenticação e autorização na rota existente do Xano.
- Permitir que Contas de Acesso ativas com perfil Paciente autentiquem e consultem somente Prontuários próprios, mantendo o vínculo e a liberação clínica validados nas rotas Xano de dados.
- Criar o roteamento comum para módulos conectados de Pacientes, Profissionais, Prontuários, Procedimentos e Nova Consulta; módulos ausentes permanecem indisponíveis.
- Disponibilizar atalhos para Nova Consulta na Visão geral e na Agenda para Administrador e Recepcionista quando o módulo estiver integrado.

Fora do escopo: criar rotas novas ou alterar contratos de dados; cadastrar, editar ou inativar Pacientes; exibir detalhes, CPF, telefone, consultas ou dados clínicos na listagem; e usar dados da demonstração no modo conectado. A autorização de perfil Paciente é adicionada somente às rotas existentes de autenticação e identidade.

## Capabilities

### New Capabilities

- `interface-pacientes`: listagem conectada de cadastros ativos com busca nominal e estados de carregamento, erro e vazio.
- `roteamento-equipe-conectada`: resolução protegida de módulos conectados, indisponibilidade segura de módulos ausentes e navegação contextual para Nova Consulta.

### Modified Capabilities

Nenhuma.

## Impact

- Streamlit: novo módulo isolado `sorrisomais/pagina_pacientes_xano.py`, mapa de módulos e despacho no menu e nas áreas Visão geral/Agenda.
- API: a listagem reutiliza `ClienteXano.listar_opcoes_agenda` (GET `/agenda/opcoes`) sem alterar esse contrato. As rotas existentes `/auth/login` e `/auth/me` passam a aceitar Conta de Acesso ativa com perfil Paciente; as rotas de dados clínicos continuam exigindo vínculo ativo e limitando o conteúdo ao próprio Paciente e aos registros liberados.
- Verificação: testes da interface com cliente simulado, sem requisições de rede.
