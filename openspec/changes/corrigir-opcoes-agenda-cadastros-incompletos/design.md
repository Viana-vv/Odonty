## Context

Ver `proposal.md`. O cliente valida nomes não vazios nas três coleções de opções. Não convém relaxar o contrato e apresentar seletores sem rótulos.

## Goals / Non-Goals

**Goals:** devolver opções utilizáveis e testar os fluxos reais solicitados.

**Non-Goals:** alterar cadastros, histórico ou escrita de reservas.

## Decisions

- Filtrar registros sem nome na consulta Xano de cada coleção. Para Profissional, também exigir CRO preenchido e identificador positivo de Especialidade. Manter situação ativa, projeção e ordem existentes.
- Preservar a listagem administrativa completa de Profissionais, que já sinaliza cadastro incompleto; o filtro pertence às opções operacionais.
- Verificar as telas com conta fictícia administrativa e de recepção, sem enviar agendamento real; sucesso de escrita e conflitos permanecem cobertos pelos testes sem rede existentes.

## Risks / Trade-offs

- [Cadastro deixar de ser selecionável] → efeito intencional para cadastro incompleto, que permanece visível na gestão.
- [Outras causas nas telas] → verificar os fluxos reais e corrigir falhas comprovadas dentro do escopo pedido.

## Migration Plan

Publicar somente a rota alterada após prévia, testar os perfis e inativar somente Contas de Acesso fictícias da verificação após logout.
