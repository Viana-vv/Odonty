## Why

A área Profissionais mostra apenas nomes porque o contrato disponível para a Agenda retorna dados mínimos. Administrador precisa consultar os dados cadastrais existentes e ativar ou inativar um Profissional; Recepcionista mantém acesso somente de leitura. A inativação deve preservar o histórico e impedir novos agendamentos.

## What Changes

- Fornecer uma listagem administrativa de Profissionais ativos e inativos com os campos cadastrais existentes e sem dados de Conta de Acesso.
- Permitir ao Administrador alterar a situação entre ativo e inativo, com autorização validada no Xano.
- Exibir cartões completos e a ação de situação na interface responsiva; Recepcionista consulta sem poder alterar.
- Preservar consultas, disponibilidades e demais referências históricas ao inativar.

## Capabilities

### New Capabilities
- `gestao-profissionais`: consulta administrativa de dados cadastrais e alteração da situação de Profissional.

### Modified Capabilities

## Impact

Afeta o cliente REST em `sorrisomais/api.py`, a tela `pagina_profissionais_xano.py`, exportações Xano para listagem e alteração de situação, e testes de contrato Python/JavaScript e interface. O export descreve o contrato a ser aplicado; a instância Xano não pode ser atualizada sem credenciais disponíveis.
