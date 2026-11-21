## Why

Hoje o Administrador não consegue criar uma Conta de Acesso de Recepcionista pela aplicação, o que obriga a configuração manual no Xano. A clínica precisa de um fluxo administrativo protegido para cadastrar esse perfil sem permitir a escolha arbitrária de privilégios.

## What Changes

- Adicionar ao painel do Administrador uma ação de cadastro de Recepcionista com nome, e-mail, senha inicial e confirmação da senha.
- Criar uma operação REST dedicada que grave somente uma Conta de Acesso ativa com o perfil fixo `recepcionista`.
- Validar sessão administrativa, campos obrigatórios, formato e unicidade do e-mail e limites da senha no Xano.
- Tratar sucesso, duplicidade, sessão expirada, acesso negado, falha de conexão e resposta inválida sem expor credenciais.
- Manter fora do escopo a edição de perfis, a criação de Administradores e a redefinição de senha.

## Capabilities

### New Capabilities

- `cadastro-recepcionista`: cadastro administrativo de uma Conta de Acesso com perfil fixo de Recepcionista, incluindo formulário, contrato REST, autorização e tratamento seguro de credenciais.

### Modified Capabilities

Nenhuma.

## Impact

- Streamlit: navegação administrativa, formulário/modal de cadastro e cliente REST.
- Xano: novo endpoint `POST /contas-acesso/recepcionistas` usando a tabela `conta_acesso` e autorização exclusiva de Administrador.
- Testes: contrato unitário separado em Python e JavaScript, além de testes de interface e permissões.
- Riscos: criação de conta com privilégio indevido, duplicidade de e-mail e exposição da senha em estado, resposta ou log; todos devem ser bloqueados pelo contrato e pelo Xano.
