## Context

Ver `proposal.md` para o diagnóstico. A listagem usa o cliente de opções de agendamento e valida as três coleções, embora exiba somente Pacientes. Cadastro e edição já invalidam o namespace `pacientes` no cache privado.

## Goals / Non-Goals

**Goals:** isolar a leitura administrativa e preservar sessão, busca, atualização manual e edição.

**Non-Goals:** alterar tabelas, corrigir cadastros existentes, flexibilizar validações ou modificar agendamento.

## Decisions

- Criar GET `/pacientes` no grupo Sorriso Acesso, reutilizando validação de sessão e autorização administrativa existentes. Consultar somente a tabela Paciente, filtrar situação `ativo`, ordenar por nome e identificador e projetar `id` e `nome`. Resposta: `{"pacientes": [...]}`, `Cache-Control: no-store` e histórico de execução desabilitado. Sem entradas de usuário e sem mudança de schema.
- Adicionar `listar_pacientes` ao cliente com validação estrita e usar namespace `pacientes` na tela. Manter os contratos da Agenda intactos. Ignorar profissionais inválidos no cliente antigo esconderia a dependência; a rota exclusiva elimina a causa.
- Manter a invalidação após cadastro/edição, sem fallback para opções da Agenda. Testar interface com opções da Agenda configuradas para falhar e listagem de Pacientes disponível.

## Risks / Trade-offs

- [Frontend usar rota ainda ausente] → publicar e verificar a nova rota antes de disponibilizar o frontend.
- [Exposição de dados] → projeção mínima e autorização no Xano; testes sem rede e sem dados reais.
- [Cache antigo] → namespace próprio impede reaproveitar a resposta antiga de `agenda/opcoes`.

## Migration Plan

Publicar apenas o novo endpoint, verificar acesso administrativo e recusa dos demais perfis e disponibilizar o frontend. Para rollback do frontend, reverter o commit; a rota adicional pode permanecer sem alterar dados nem contratos anteriores.
