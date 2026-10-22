# Proposta: listagem conectada de Profissionais

## Por quê

A área Profissionais ainda utiliza os dados da demonstração. A equipe administrativa precisa consultar os Profissionais ativos retornados pelo Xano.

## O que muda

- Exibir na área Profissionais os nomes retornados por `ClienteXano.listar_opcoes_agenda` (`GET /agenda/opcoes`).
- Apresentar carregamento, erro e estado vazio, em uma composição responsiva inspirada em `05-profissionais.png`.
- Limitar os dados exibidos a identificador e nome conforme o contrato existente. Não adicionar rotas, cadastro, perfil, edição ou campos.

## Impacto

Novo módulo Streamlit para a listagem e testes de interface sem rede. O endpoint existente já restringe o retorno a Profissionais ativos e autoriza Administrador e Recepcionista no Xano; não há alteração de contrato ou backend.
