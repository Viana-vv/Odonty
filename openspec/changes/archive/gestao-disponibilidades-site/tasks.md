# Tasks

## 1. Confirmar contratos e permissões

- [x] 1.1 Conferir o payload, a resposta e as permissões do `POST /disponibilidades` no cliente e no export Xano; corrigir eventual defeito impeditivo e verificar a rota sem alterar dados reais.
- [x] 1.2 Confirmar o carregamento de Profissionais ativos permitido a Administração e Recepção e registrar os contratos reutilizados no escopo da implementação.

## 2. Integrar formulário à Agenda

- [x] 2.1 Adicionar ação e formulário de cadastro de uma Disponibilidade para Administração e Recepção, seguindo o kit Sorriso Mais; verificar a exibição por perfil e os controles renderizados nos testes de interface.
- [x] 2.2 Validar campos obrigatórios no formulário e enviar o intervalo pelo cliente Xano; verificar que sucesso atualiza a Agenda e que conflito, erro e resposta inválida mostram mensagens sem falso sucesso.

## 3. Cobertura dos contratos e verificação

- [x] 3.1 Garantir testes unitários Python separados para cada rota GET/POST usada no fluxo, verificando rota, método, payload/resposta e erros sem rede; executar os testes.
- [x] 3.2 Garantir testes unitários JavaScript separados para cada rota GET/POST usada no fluxo, verificando correspondência entre rota, método e export Xano sem rede; executar os testes.
- [x] 3.3 Validar a change com `openspec validate gestao-disponibilidades-site --strict` e verificar os cenários de cadastro, conflito, API indisponível e autorização.
