## Context

Além da dependência descrita em `proposal.md`, o usuário esclareceu que a Recepcionista não consegue acessar o catálogo. Menu, tela e especificação antiga o restringiam ao Administrador. A solicitação atual autoriza consulta também pela Recepcionista, coerente com as atividades administrativas do domínio.

## Goals / Non-Goals

**Goals:** permitir leitura mínima do catálogo por Administrador e Recepcionista, independente das demais listas.

**Non-Goals:** criar ou editar Procedimentos, expor informações clínicas ou alterar permissões de outros perfis.

## Decisions

- Criar GET `/procedimentos` usando validação de sessão e verificação de perfil administrativo ativo no Xano. Consultar somente Procedimentos ativos, ordenados por nome/identificador, com projeção de `id` e `nome`, `Cache-Control: no-store` e histórico desabilitado.
- Adicionar cliente estrito e usar namespace `procedimentos` no cache. Manter busca local, atualização manual, estados vazios e tratamento de erros.
- Liberar o menu e a tela somente para Administrador e Recepcionista. A autorização efetiva permanece no backend; Paciente e Profissional não recebem o catálogo administrativo.

## Risks / Trade-offs

- [Ampliação de acesso] → somente leitura de identificador e nome, autorizada expressamente pelo usuário após esclarecimento.
- [Frontend chamar rota ausente] → publicar somente a rota nova e verificar antes de concluir.

## Migration Plan

Editar a `main` local conforme autorização vigente. Publicar a nova rota com prévia, verificar autenticação administrativa e recusa dos outros perfis. Sem migração de dados.
