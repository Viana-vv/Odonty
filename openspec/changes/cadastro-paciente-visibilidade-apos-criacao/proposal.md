# Proposta: Atualizar a lista após cadastrar Paciente

## Problema

A listagem conectada mantém Pacientes em cache por até 20 segundos na sessão. Quando o cadastro retorna sucesso, a navegação volta à lista sem invalidar esse cache; por isso, o Paciente recém-criado pode não aparecer e a equipe pode interpretar a operação como falha.

## Escopo

- Invalidar o cache da listagem de Pacientes somente depois de o POST ser confirmado como sucesso.
- Preservar a chave e o payload da operação quando o resultado do POST for incerto.

## Fora do escopo

- Alterar contrato REST, endpoint Xano, permissões, modelo de dados ou idempotência.
- Alterar outros caches ou telas sem dependência da lista de Pacientes.

## Dependências e riscos

A invalidação deve usar a API de cache compartilhado quando disponível. A mudança não pode invalidar em timeout, resposta incompatível ou rejeição definitiva, pois esses casos não confirmam criação.
