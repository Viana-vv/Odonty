## Por quê

As changes de Exames, Procedimentos realizados e Reagendamento possuem contratos REST e suítes de integração Xano temporárias. É necessário um roteiro curto para repetir a verificação sem confundir resultados históricos, validações locais e chamadas remotas, nem alterar a API principal automaticamente.

## O que muda

- Especificar um smoke/dry-run conjunto e opt-in dos contratos recentes de Exames, Procedimentos realizados e Reagendamento.
- Exigir execução remota somente em grupo temporário segregado autorizado, com dados fictícios, limite de no máximo 10 requisições em qualquer janela de 20 segundos e espera entre chamadas.
- Cobrir autenticação/autorização, validação, recurso inexistente, conflito e rollback transacional quando aplicável; remover ou inativar somente artefatos temporários criados e autorizados pela execução.
- Separar evidência local sem rede de evidência Xano; não publicar nem alterar produção automaticamente.

Fora de escopo: mudança de endpoints ou regras de negócio, publicação, migração de dados, mutação do grupo principal e uso de dados reais.

## Impacto

Somente documentação e execução de verificações existentes. A validação remota depende das credenciais administrativas de Metadata, da identificação do workspace e da disponibilidade de grupo temporário segregado.
