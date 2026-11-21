## Context

Ver o diagnóstico em `proposal.md`. GET `/profissionais` acessa os atributos da especialidade mesmo quando o vínculo não existe; o cliente exige nome e CRO preenchidos em todos os itens. Reagendamento valida também Procedimentos de GET `/agenda/opcoes`, embora não os utilize.

## Goals / Non-Goals

**Goals:** manter visíveis registros incompletos para gestão e liberar leitura dos demais, isolando opções do reagendamento.

**Non-Goals:** inventar nomes ou CROs, inativar registros, alterar transações de agendamento ou ampliar permissões.

## Decisions

- No Xano, retornar diretamente a projeção `id`/`nome` de Especialidade ou `null`, sem acessar atributos do vínculo inexistente. Nome e CRO continuam strings obrigatórias no contrato; strings vazias representam cadastro legado incompleto. O cliente continua recusando identificadores inválidos, duplicados, tipos inesperados e situação desconhecida.
- Na tela de Profissionais, mostrar o identificador quando o nome estiver vazio, campos ausentes como não informados e aviso de cadastro incompleto. Não descartar registros da listagem administrativa nem modificar sua situação.
- No reagendamento, carregar GET `/pacientes` e GET `/profissionais` com namespaces próprios. Filtrar opções de destino por situação ativa, nome/CRO preenchidos e especialidade presente; informar a existência de cadastros incompletos. Não chamar as opções da Agenda nem Procedimentos.
- Manter a validação efetiva de sessão, perfil, disponibilidade e conflito no Xano. O filtro do seletor não substitui autorização nem altera contratos de escrita.

## Risks / Trade-offs

- [Cliente anterior rejeitar cadastro incompleto] → disponibilizar o cliente atualizado junto da tela; o formato válido anterior permanece compatível.
- [Cadastro incompleto ocultado] → preservar cartão e identificador com aviso explícito; somente a seleção de destino o exclui.

## Migration Plan

Aplicar a correção local na `main`, conforme orientação do usuário; publicar apenas GET `/profissionais` após prévia. Verificar com Conta de Acesso fictícia de Recepcionista, sem alterar consultas existentes. Não há migração de dados.
