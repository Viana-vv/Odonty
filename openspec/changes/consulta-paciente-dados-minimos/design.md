## Context

Ver [proposal.md](proposal.md) para a motivação e [specs/consultas/spec.md](specs/consultas/spec.md) para o contrato observável. Hoje o endpoint compõe os dados de Procedimento ao formatar as Consultas. A autorização e a redução de dados precisam ocorrer no Xano; a resposta da equipe constitui compatibilidade existente.

## Goals / Non-Goals

**Goals:**

- Decidir o perfil antes da serialização final e produzir um formato mínimo próprio para Paciente, incluindo apenas os identificadores de contexto necessários e o nome do Profissional exibido pela tela.
- Evitar consultas auxiliares de Procedimentos quando o perfil não pode receber seus dados.
- Preservar a forma completa atual usada pela equipe.

**Non-Goals:**

- Alterar navegação, telas, filtros, regras de autorização existentes ou dados persistidos.
- Declarar validado o endpoint remoto Xano sem revisão segura do grupo.

## Decisions

- **Separar a serialização por perfil no Xano.** Após aplicar autenticação e escopo existentes, a ramificação Paciente constrói o item mínimo sem ler ou serializar Procedimentos; os demais perfis seguem pelo caminho atual. Isso reduz exposição na origem e evita depender do frontend para filtrar dados. Alternativa considerada: retornar a resposta integral e filtrar no cliente; rejeitada porque o frontend não é mecanismo de segurança.
- **Fixar a fronteira de dados em testes de contrato sem rede.** O cliente aceita o nome do Paciente ausente, mas continua exigindo o nome do Profissional usado na tela. Os testes conferem a resposta mínima do Paciente e que os campos de Procedimentos continuam previstos no caminho da equipe. A inspeção do script Xano local não substitui a validação da execução no Xano real.

## Risks / Trade-offs

- [O Xano remoto pode divergir do arquivo `.xs` versionado] → validar a edição e a resposta em ambiente seguro do grupo antes de considerar a mudança efetiva.
- [Consumidores de Paciente podem depender de campos atualmente recebidos] → revisar o contrato dos testes do cliente e atualizar apenas o tratamento de dados compatível com a lista mínima aprovada, sem alterar navegação.
- [Contas com múltiplos perfis podem tornar a precedência ambígua] → manter a precedência atual do endpoint, em que a ramificação Paciente é aplicada primeiro, e cobri-la no teste de contrato.

## Migration Plan

1. Atualizar o endpoint versionado e os testes unitários locais.
2. Em grupo seguro, comparar o endpoint remoto com a change e validar respostas de Paciente e equipe usando contas de teste autorizadas.
3. Reverter a publicação do endpoint no Xano para a versão anterior caso a resposta da equipe ou o escopo do Paciente não corresponda aos cenários.

