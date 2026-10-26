## Context

O portal já usa uma sessão isolada em `sessao_paciente.py` e os contratos Xano existentes de login e identidade. A equipe entra por `app.py`; o portal do Paciente usa `portal_paciente.py`. O layout visual existente em `assets/estilos.css` foi criado originalmente para a tela da equipe e os seletores atuais não estilizam os widgets do portal.

## Goals / Non-Goals

**Goals:** corrigir o fluxo de login de ponta a ponta sem conceder acesso localmente; dar ao portal um formulário visual coerente com o kit Sorriso Mais; remover a frase solicitada; mostrar erros seguros e operáveis.

**Non-Goals:** criar ou alterar Contas de Acesso no Xano, redefinir senha, tornar o portal parte do login da equipe ou adicionar novas rotas.

## Decisions

- Manter `POST /auth/login` e `GET /auth/me` como fonte de autenticação e perfil. Investigar formato e tratamento de respostas nos dois passos; alterar o contrato Xano somente se a diferença entre export local e endpoint publicado for comprovada.
- Manter credenciais apenas em `st.session_state` durante a submissão e a sessão. Não manter senha após sucesso ou falha, nem incluí-la em mensagens/logs.
- Criar uma composição própria de login no módulo do Paciente usando componentes Streamlit e estilos com chaves específicas do portal. Em telas estreitas, empilhar as colunas; não modificar os estilos globais da equipe.
- Diferenciar credenciais rejeitadas/perfil sem acesso de indisponibilidade de rede sem revelar dados da Conta de Acesso. O conteúdo protegido continua condicionado à identidade confirmada pelo Xano.

Alternativas consideradas: reutilizar a tela da equipe, o que mistura as duas superfícies de acesso; substituir o login Xano por uma verificação no frontend, o que enfraqueceria a segurança; manter o layout atual, que não satisfaz a referência visual do kit.

## Risks / Trade-offs

- A conta pode autenticar, mas não estar vinculada a um cadastro de Paciente; isso deve ser distinguido de falha de login sem exibir dados de terceiros.
- O endpoint publicado pode diferir do XanoScript versionado; comparar e validar antes de alterar o Xano.
- CSS de Streamlit depende da estrutura dos widgets; cobrir renderização responsiva e interação com AppTest e inspeção visual.

## Migration Plan

Não há migração de dados nem mudança de tabelas. Publicar a aplicação após validação do login e da interface. O retorno à versão anterior consiste em reverter somente a mudança da tela/sessão.
