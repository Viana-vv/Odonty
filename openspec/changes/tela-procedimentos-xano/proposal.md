# Catálogo conectado de Procedimentos

## Por quê

A tela de Procedimentos existente usa dados demonstrativos. A equipe administrativa precisa consultar os Procedimentos disponíveis no catálogo autorizado pelo Xano.

## O que muda

- Apresentar uma tela conectada, somente para leitura, seguindo a referência `07-procedimentos.png`.
- Carregar opções pelo método existente `ClienteXano.listar_opcoes_agenda`, exibindo somente o identificador como chave interna e o nome como conteúdo visível.
- Tratar carregamento, erro, catálogo vazio e busca, com composição responsiva.

## Limites

- Não criar, editar ou inativar Procedimentos.
- Não presumir preço, duração, categoria, situação ou outra rota.
- A autorização do catálogo permanece no Xano para Administrador e Recepcionista.
