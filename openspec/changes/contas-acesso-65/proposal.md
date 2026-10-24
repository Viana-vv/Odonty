## Por quê

A equipe administrativa precisa consultar as Contas de Acesso cadastradas sem expor credenciais ou permitir alterações por esta tela.

## O que muda

- Criar listagem somente leitura de Contas de Acesso para Administrador e Recepcionista.
- Criar `GET /contas-acesso`, protegido por sessão válida e autorização no Xano, retornando exclusivamente `id`, `nome`, `email`, `perfis` e `situacao`.
- Exibir carregamento, lista, resposta vazia, falha e acesso negado em módulo Streamlit próprio.

Fora do escopo: criação, edição, ativação/inativação, gestão de perfil ou credencial, mudanças no cliente compartilhado e integração na navegação.

## Capacidade

- Nova: `consulta-contas-acesso` — listagem administrativa segura e somente leitura.

## Impacto

- Frontend: novo módulo `sorrisomais/pagina_contas_acesso_xano.py`.
- Integração HTTP: módulo próprio e injetável que usa o transporte existente, sem editar `sorrisomais/api.py`.
- Backend: novo export Xano GET em `backend/xano/api/sorriso_acesso/contas_acesso_GET.xs`.
- Testes Python e JavaScript separados por rota, além de testes da tela Streamlit sem rede.
