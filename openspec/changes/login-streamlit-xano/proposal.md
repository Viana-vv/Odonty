## Why

O Sorriso+ precisa de uma entrada autenticada na arquitetura aprovada, com identidade e autorização controladas pelo Xano. Esta change limita a primeira entrega ao login, à sessão, ao logout e ao acesso inicial protegido.

## What Changes

- Criar interface Streamlit em português brasileiro com identidade Sorriso+, tons verdes e referência na imagem `1000323602.jpg`.
- Integrar autenticação real por e-mail e senha, identificação da Conta de Acesso e autorização via API REST do Xano, com contrato proposto de login, consulta da própria identidade e logout detalhado no design, sujeito à revisão.
- Tratar validação de campos, envio em andamento, credenciais incorretas, respostas inválidas, indisponibilidade e expiração.
- Documentar configuração, execução e verificações simuladas e reais.
- Propor sessão de uma hora sem renovação, revogação por sessão no Xano e matriz limitada à identificação própria dos três perfis internos. Preservar eventual protótipo fornecido posteriormente; o usuário confirmou que não há protótipo disponível.

Fora do escopo: funcionalidades clínicas e administrativas, migração de dados, Drizzle/D1, persistência de negócio em localStorage, cadastro e recuperação de senha sem fluxo aprovado e backend real. A senha demonstrativa mencionada no pedido não será autenticação real.

## Capabilities

### New Capabilities

- `acesso-autenticado`: login, identidade, sessão, logout e acesso inicial autorizado no Sorriso+.

### Modified Capabilities

Nenhuma: não havia specs nem changes existentes na inspeção inicial.

## Impact

Introduz futuramente a aplicação Python/Streamlit e a integração REST. Propõe três endpoints e estruturas de Conta de Acesso e Sessão de Acesso no Xano, detalhados no design. São propostas, não estruturas existentes comprovadas; dependem de aprovação e inspeção para reutilizar dados compatíveis.

Estado: rascunho para revisão, bloqueado para implementação dos comportamentos pendentes. Os documentos de contexto existem; o README foi preparado nesta etapa. `app/page.tsx`, `app/globals.css` e arquivos de hospedagem não estão disponíveis nesta cópia. A imagem local foi analisada e será a referência visual disponível.

O usuário confirmou que não há protótipo, contrato REST ou matriz aprovados. Posteriormente aprovou login por e-mail e senha e página inicial somente com nome, perfil retornado pelo backend e botão Sair, sem dados clínicos. Aprovou manter Profissional no domínio, Dentista como rótulo e somente os três perfis internos nesta change. Contrato, matriz inicial e política de sessão foram propostos no design a pedido do usuário. Dependências: revisar essas propostas, inspecionar a estrutura existente e configurar e verificar o Xano. A matriz distingue os três perfis, com igual acesso limitado à própria identificação nesta change. A tentativa de conexão anterior nesta sessão terminou em timeout, o que não comprova indisponibilidade permanente.

O Git está na branch `fix/telaLogin/2313`. O vínculo com Issue e a revisão por outro integrante precisam ser confirmados. Nenhuma Issue ou PR foi criada nesta etapa.



