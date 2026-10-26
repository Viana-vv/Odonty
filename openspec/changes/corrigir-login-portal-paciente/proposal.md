## Why

O login do Paciente está falhando mesmo para uma Conta de Acesso ativa, e a tela atual não apresenta bem a identidade visual do projeto. A frase que remete a equipe a outro endereço também deve sair do portal.

## What Changes

- Investigar e corrigir o fluxo de autenticação do Paciente com o Xano, preservando a validação do perfil e da sessão.
- Remover a frase “Acesso pessoal do Paciente. A equipe utiliza outro endereço.”
- Melhorar a tela de login do Paciente seguindo o kit Sorriso Mais e mantendo os controles acessíveis e responsivos.
- Apresentar mensagens seguras para credenciais rejeitadas, conta sem autorização e indisponibilidade.

Fora do escopo: criar Conta de Acesso, redefinir senha, alterar perfis no Xano ou permitir login de Paciente no endereço da equipe.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `acesso-autenticado`: esclarecer a entrada independente do Paciente e os requisitos visuais e de erro de seu login.

## Impact

- `sorrisomais/autoatendimento_paciente.py` e `sorrisomais/sessao_paciente.py`.
- CSS da tela do Paciente em `assets/estilos.css`.
- Testes Streamlit e de sessão; contratos Xano existentes permanecem sem alteração, salvo se a investigação demonstrar defeito comprovado no endpoint.
- Nenhuma alteração de schema ou criação de dados no Xano prevista.
