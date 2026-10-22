# Tela de histórico individual do Prontuário

## Objetivo

Conectar a tela de histórico individual do Prontuário ao Xano, apresentando Registros Clínicos e Consultas retornados dentro do escopo da Conta de Acesso autenticada.

## Escopo

- Usar `GET /consultas` e `GET /registros-clinicos` para montar a seleção e o histórico individual do Prontuário.
- Ajustar o export Xano existente de `GET /registros-clinicos` para que os filtros opcionais não alterem nem ampliem o escopo autenticado.
- Garantir que o Profissional consulte somente Registros Clínicos associados ao seu próprio vínculo e que o Paciente consulte somente os próprios Registros liberados.
- Preservar autenticação, validação de sessão, resposta sem cache e os metadados Xano do endpoint e da tabela `registro_clinico`.
- Apresentar estados de carregamento, erro, lista vazia e histórico vazio.
- Restringir a apresentação clínica na interface a Contas com perfil Paciente ou Profissional, mantendo o Xano como autoridade de autorização.

## Fora do escopo

- Criar endpoint alternativo, novo mecanismo de autenticação ou nova entidade de dados.
- Criar, retificar ou excluir Registros Clínicos na tela individual.
- Apresentar nomes de Profissionais, Consultas ou datas que não estejam disponíveis nos contratos consumidos.
