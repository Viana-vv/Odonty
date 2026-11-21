## Why

O cadastro de Profissional depende de Especialidades previamente configuradas, mas a aplicação apenas lista registros existentes e orienta o Administrador a configurá-los manualmente no Xano. É necessário permitir que o próprio Administrador cadastre novos tipos de Especialidade pela interface.

## What Changes

- Adicionar ao painel do Administrador uma ação de cadastro de Especialidade com nome obrigatório.
- Criar uma operação REST dedicada para cadastrar a Especialidade como ativa e disponibilizá-la na seleção do cadastro de Profissional.
- Validar sessão administrativa, conteúdo do nome e duplicidade após normalização no Xano, inclusive sob envios concorrentes.
- Atualizar o cache da interface após sucesso para que a nova Especialidade apareça sem exigir configuração manual no Xano.
- Tratar campos inválidos, duplicidade, sessão expirada, acesso negado, falha de conexão e resposta inválida com mensagens seguras.
- Manter fora do escopo a edição, inativação, exclusão e associação de múltiplas Especialidades a um Profissional.

## Capabilities

### New Capabilities

- `cadastro-especialidade`: cadastro administrativo de um novo tipo de Especialidade, incluindo formulário, contrato REST, autorização, unicidade e atualização das opções do cadastro de Profissional.

### Modified Capabilities

Nenhuma.

## Impact

- Streamlit: navegação administrativa, formulário/modal, cliente REST e invalidação do cache de Especialidades.
- Xano: novo endpoint `POST /especialidades` e garantia de unicidade normalizada na tabela `especialidade`.
- Integração existente: `GET /especialidades` e o formulário de cadastro de Profissional passam a refletir os novos registros ativos.
- Testes: contrato unitário separado em Python e JavaScript, além de testes de interface, validação e permissões.
- Riscos: nomes duplicados por diferenças de caixa ou espaços e inconsistência de cache; a normalização e a invalidação após sucesso devem evitá-los.
