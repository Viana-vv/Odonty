## Why

O Administrador precisa cadastrar um Dentista pela aplicação e permitir que ele entre com sua própria Conta de Acesso. Hoje o acesso da equipe oferece somente identificação e saída, sem cadastro pelo sistema.

## What Changes

- Manter o login exclusivo da equipe, separado do futuro login de Paciente.
- Apresentar página do Administrador com a opção Cadastrar profissional.
- Criar página exclusiva de cadastro de Dentista com nome, e-mail, senha inicial, confirmação, CRO e seleção de especialidade existente.
- Criar API protegida no Xano, exclusiva de Administrador ativo com sessão válida, que cria Profissional e Conta de Acesso vinculados.
- Permitir login do Dentista criado, mantendo sua página de identificação e saída nesta entrega, separada da página administrativa.
- Fixar o perfil criado em profissional; o recorte confirmado não inclui cadastrar Administrador ou Recepcionista nem seletor desses perfis.

Fora do escopo: cadastro e login de Paciente, criação de outros perfis, painéis clínicos, agenda, edição/inativação/listagem de profissionais, recuperação e troca obrigatória de senha. Somente dados fictícios.

## Capabilities

### New Capabilities
- `cadastro-profissional`: cadastro de Dentista por Administrador e criação vinculada de sua Conta de Acesso.

### Modified Capabilities
- `acesso-autenticado`: página inicial administrativa com acesso ao cadastro, mantendo login da equipe e restrições dos demais perfis.

## Impact

Interface Streamlit, cliente REST e testes; nova operação no Xano e estrutura de Profissional vinculada à conta existente. Preservar tabelas e APIs legadas; inspecionar metadados remotos antes de escolher a estrutura física. Não modificar manualmente specs principais.

Riscos principais: criação parcial de conta/profissional, duplicação concorrente de e-mail/CRO, elevação de perfil e exposição da senha inicial. O design propõe transação, unicidade no backend, perfil fixo e ausência de segredos em logs/respostas.

Escopo funcional confirmado pelo usuário. Apply autorizado pelo usuário; adaptação à tabela legada e seleção de especialidade existente também aprovadas.

Issue: https://github.com/Viana-vv/Odonty/issues/3. Branch: feat/3-cadastro-profissional-admin.
