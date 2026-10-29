# Design

A tela recebe `cliente` e `token` fornecidos pela sessão autenticada e chama o método existente `listar_consultas(token)`. O endpoint deve restringir as Consultas ao Paciente associado à Conta de Acesso; a interface não envia identificador de Paciente. A classificação entre futuras e passadas usa `inicio_em` no fuso de São Paulo. A visualização reaproveita a hierarquia simples do kit Sorriso Mais, com título, seletor e cartões responsivos. Erros de acesso mostram mensagem compreensível; nenhum dado clínico ou procedimento é exibido.
