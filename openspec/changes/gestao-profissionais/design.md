## Context

A tabela `profissional` já armazena nome, CRO, especialidade, e-mail, telefone, situação e datas; `situacao` usa `Ativo`/`Inativo`. O contrato de `/agenda/opcoes` deliberadamente retorna apenas ID/nome. A criação de Consulta já exige Profissional Ativo. Veja `proposal.md` para motivação e `specs/gestao-profissionais/spec.md` para comportamento.

## Goals / Non-Goals

**Goals:** Fornecer contratos administrativos mínimos, validar situação no Xano e atualizar os cartões com dados que o modelo realmente fornece.

**Non-Goals:** Alterar o modelo físico, dados de Contas de Acesso, regras de cadastro, disponibilidade, Consulta ou o contrato enxuto da Agenda.

## Decisions

- Criar `GET /profissionais` para Administrador e Recepcionista. Retornar cadastros ativos e inativos ordenados por nome/ID, com `id`, `nome`, `cro`, `especialidade: {id,nome}`, `email`, `telefone` e situação normalizada (`ativo`/`inativo`). E-mail e telefone podem ser nulos. Excluir CPF, Conta de Acesso, tokens e conteúdo clínico.
- Criar `PATCH /profissionais/{id}/situacao`, corpo estrito `{situacao: "ativo"|"inativo"}`, autorizado apenas para Administrador ativo e com sessão válida. Retornar `{profissional: {id, situacao}}`; rejeitar identificador/situação inválidos e devolver 404 para cadastro ausente.
- Atualizar apenas situação e `atualizado_em`; não excluir ou atualizar registros relacionados. A rota de criar Consulta permanece como controle backend para impedir novos agendamentos a inativos.
- Implementar métodos REST com validação de resposta em `api.py`; cartões exibem os campos acima. Apenas Administrador vê ação de situação e confirmação. Após sucesso, recarregar lista; após falha, mostrar mensagem segura e não apresentar valor enviado como confirmado.
- Arquivos `profissionais_GET.xs` e `profissionais_id_situacao_PATCH.xs` documentam os contratos para importação no Xano. Sem credenciais de instância nesta cópia, a mudança não pode ser implantada remotamente.
- Manter cartões responsivos do módulo existente. A imagem de referência 05 não está presente nesta cópia; respeitar o kit e a composição atual sem inventar campos.

## Risks / Trade-offs

- [Instância Xano ainda sem as rotas novas] → O cliente receberá erro até que os exports sejam aplicados; informar esse requisito e testar contratos sem rede.
- [Dados opcionais podem estar vazios] → Representar ausências como “Não informado”, sem fabricar valores.
- [Inativação acidental] → Exigir confirmação e manter autorização/validação no backend.

## Migration Plan

Aplicar primeiro os exports Xano e validar respostas por contas Administrador e Recepcionista; depois publicar o cliente Streamlit. Rollback: reverter cliente e exports das rotas novas. A alteração de situação já gravada não é revertida automaticamente; Administrador pode reativar o cadastro pelo mesmo contrato.
