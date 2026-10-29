## Why

Os contratos de Agenda e Disponibilidades já estão representados no código-fonte versionado, mas não há evidência local de que as rotas atuais estejam publicadas no workspace Xano compartilhado. A publicação e a validação no grupo principal são necessárias para tornar esses fluxos disponíveis à aplicação conectada.

## What Changes

- Publicar no grupo Xano `Sorriso Acesso` os contratos versionados de listagem da Agenda e das Disponibilidades, cadastro e atualização de Disponibilidade.
- Confirmar no workspace publicado autenticação, autorização, serialização e tratamento de conflito usando somente dados fictícios e dentro do limite de requisições.
- Registrar a evidência da publicação e os resultados da verificação sem incluir credenciais nem dados pessoais.
- Na finalização de Agenda e Nova Consulta autorizada em 29/10/2026, corrigir a data inicial da tela própria para usar a seleção da Agenda e o retorno imediato à Agenda ao cancelar, conforme o kit visual. Preservar a data do filtro enquanto o formulário é editado.

Fora do escopo: outras alterações funcionais da interface Streamlit, mudanças de domínio ou criação de novos contratos REST.

## Capabilities

Esta mudança publica contratos já especificados e corrige comportamentos já documentados de navegação e data inicial do formulário. Não introduz novos requisitos nas capacidades existentes; portanto, usa `skip_specs: true`.

## Impact

- Fontes Xano: `consultas_GET.xs`, `disponibilidades_GET.xs`, `disponibilidades_POST.xs` e `disponibilidades_id_PATCH.xs`.
- Workspace e grupo publicados do Xano, via Metadata API autenticada.
- Testes locais dos contratos existentes e verificação opt-in no grupo publicado.

Dependência: credencial administrativa da Metadata API e identificador do workspace disponibilizados por configuração segura. Sem eles, não é possível publicar nem afirmar o estado do workspace.
