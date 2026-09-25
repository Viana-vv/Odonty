## Why

O Sorriso+ precisa de uma entrada autenticada na arquitetura aprovada, com identidade e autorização controladas pelo Xano. Esta change limita a primeira entrega ao login, à sessão, ao logout e ao acesso inicial protegido.

## What Changes

- Criar interface Streamlit em português brasileiro com identidade Sorriso+, tons verdes e referência na imagem `1000323602.jpg`.
- Integrar autenticação real por e-mail e senha, identificação da Conta de Acesso e autorização via API REST do Xano, com contrato aprovado de login, consulta da própria identidade e logout detalhado no design.
- Tratar validação de campos, envio em andamento, credenciais incorretas, respostas inválidas, indisponibilidade e expiração.
- Documentar configuração, execução e verificações simuladas e reais.
- Implementar sessão de uma hora sem renovação, revogação por sessão no Xano e matriz limitada à identificação própria dos três perfis internos. Preservar eventual protótipo fornecido posteriormente; o usuário confirmou que não há protótipo disponível.

Fora do escopo: funcionalidades clínicas e administrativas, migração de dados, Drizzle/D1, persistência de negócio em localStorage, cadastro e recuperação de senha sem fluxo aprovado e backend real. A senha demonstrativa mencionada no pedido não será autenticação real.

## Capabilities

### New Capabilities

- `acesso-autenticado`: login, identidade, sessão, logout e acesso inicial autorizado no Sorriso+.

### Modified Capabilities

Nenhuma: não havia specs nem changes existentes na inspeção inicial.

## Impact

A aplicação Python/Streamlit, o cliente REST, o controle de sessão e os arquivos XanoScript estão implementados. A integração foi validada por 25 testes reais no Xano, além de 54 testes locais e verificação do fluxo completo pelo navegador.

Contrato, matriz e política foram aprovados conforme registro no design. A interface limita-se à própria identificação dos três perfis internos, com Profissional exibido como Dentista. A tabela legada usuario e as APIs antigas devem ser preservadas.

Issue: https://github.com/Viana-vv/Odonty/issues/1. Branch: feat/1-login-streamlit-xano. A implementação está pronta para revisão por outro integrante. A situação das tarefas está em tasks.md.
