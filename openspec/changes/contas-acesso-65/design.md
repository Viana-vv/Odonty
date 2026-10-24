## Contexto

A tabela Xano `conta_acesso` armazena autenticação, incluindo o campo sensível `senha`. A consulta precisa projetar a resposta explicitamente; não é permitido serializar a linha inteira. As telas administrativas existentes protegem endpoints com validação de sessão e verificação de perfil no próprio Xano.

## Decisões

- Criar `GET /contas-acesso`, autenticado por `conta_acesso`, validar sessão e confirmar que a própria conta está ativa e tem perfil `administrador` ou `recepcionista`.
- Buscar e retornar somente `id`, `nome`, `email`, `perfis` e `situacao`; definir `Cache-Control: no-store` e `history = false`.
- A camada Python específica da tela chama o transporte `_request` existente por composição, valida a estrutura de cada registro e descarta chaves extras. Não adicionar método ao arquivo compartilhado `api.py`.
- Implementar tela em módulo independente, com verificação de perfil para experiência do usuário e mensagens para 401, 403, lista vazia e indisponibilidade. A proteção efetiva permanece no Xano.
- Seguir os cartões e cores da referência aprovada `05-profissionais.png`, sem controles de escrita. Agrupar os cartões em linhas de três, preservando a ordem natural quando as colunas empilham em telas estreitas.
- Exibir os nomes de perfil do domínio (incluindo “Profissional”) e oferecer atualização manual da consulta para recuperar erros ou refletir mudanças feitas por outras telas.
- Manter testes unitários sem requisições reais à rede; os testes JavaScript verificam o export e o contrato do endpoint.

## Riscos

- Não há configuração ou credencial para um grupo temporário Xano nesta worktree. O endpoint não foi chamado para evitar atingir uma instância possivelmente de produção; a validação automatizada do export e os testes locais verificam o contrato, e a importação em grupo temporário fica pendente.
