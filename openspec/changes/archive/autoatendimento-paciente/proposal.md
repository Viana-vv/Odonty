## Why

O Paciente ainda não tem uma superfície própria para entrar no sistema e acompanhar suas Consultas e informações que a clínica liberou. A aplicação atual atende à equipe; esta change acrescenta uma experiência separada para o Paciente, reutilizando autenticação e autorização já existentes no Xano.

## What Changes

- Criar um entrypoint Streamlit independente para autenticação e autoatendimento do Paciente, sem persistir senha ou restaurar credenciais após perda de estado.
- Impedir no entrypoint interno que uma Conta de Acesso somente Paciente abra a área da equipe; as operações internas continuam autorizadas pelo Xano.
- Reutilizar os contratos Xano existentes para exibir Consultas próprias, Registros Clínicos explicitamente liberados e Exames próprios com resultado disponível.
- Tratar sessão expirada, conta sem perfil Paciente, falha de API, listas vazias e logout com mensagens seguras.
- Aplicar a hierarquia visual, cores, componentes e responsividade do kit Sorriso Mais.

Fora do escopo: cadastro de Conta de Acesso para Paciente, recuperação de senha, agendamento ou cancelamento pelo Paciente, alteração de conteúdo clínico, novos endpoints ou mudanças de autorização no Xano.

## Capabilities

### New Capabilities
- `autoatendimento-paciente`: entrada independente do Paciente e consulta de Consultas próprias e conteúdos clínicos liberados.

### Modified Capabilities
- `acesso-autenticado`: esclarecer que o entrypoint interno permanece exclusivo da equipe e que o Paciente utiliza uma superfície separada.

## Impact

- Ajuste de `app.py` para impedir renderização da área interna para conta somente Paciente.
- Novo entrypoint Streamlit e módulos isolados de sessão/apresentação do Paciente.
- Reuso de `POST /auth/login`, `GET /auth/me`, `POST /auth/logout`, `GET /consultas`, `GET /registros-clinicos` e `GET /exames` no cliente Xano existente.
- Testes de interface/sessão sem rede e uso dos testes de contrato Python e JavaScript existentes por rota, sem chamadas reais.
- Não requer alteração de schema ou rotas Xano; os contratos existentes derivam o escopo da Conta de Acesso e limitam conteúdo liberado.
