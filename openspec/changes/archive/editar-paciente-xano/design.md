## Context

Consulte `proposal.md` e `specs/edicao-paciente/spec.md`. Hoje `GET /agenda/opcoes` retorna apenas ID e nome dos Pacientes ativos e `POST /pacientes` cadastra; não há leitura individual nem atualização cadastral. O modelo Xano possui CPF único e um campo `observacoes`, mas a interface administrativa não pode tratar informação clínica.

## Goals / Non-Goals

**Goals:**
- Criar consulta individual e atualização cadastral autenticadas no Xano, com autorização de Administrador/Recepcionista no backend.
- Conectar ambas as operações ao cliente REST Python e oferecer edição compatível com os padrões visuais do kit.
- Preservar relações históricas e limitar o payload à lista explícita de campos pessoais.

**Non-Goals:**
- Expor observações, Prontuário ou qualquer conteúdo clínico à tela administrativa.
- Alterar permissões gerais, cadastro, listagem de Pacientes ou outros módulos.
- Publicar remotamente endpoints sem ambiente Xano configurado e autorizado.

## Decisions

- Adicionar `GET /pacientes/{paciente_id}` e `PATCH /pacientes/{paciente_id}` ao grupo Xano existente. A consulta é necessária porque as opções da agenda não trazem dados suficientes; PATCH é apropriado para atualizar um recurso individual já identificado.
- Reutilizar validações e normalização de `sorrisomais/pacientes.py` e as mensagens genéricas do cliente. O Xano repete todas as validações, confere CPF duplicado excluindo o próprio ID e atualiza somente os seis campos aprovados.
- Restringir as duas rotas a Conta de Acesso ativa, sessão válida e perfil administrador ou recepcionista, seguindo o contrato existente de `POST /pacientes`. A autorização da UI é apenas conveniência; cada rota valida o perfil no backend.
- A consulta devolve exclusivamente `id`, `nome`, `data_nascimento`, `cpf`, `telefone`, `celular` e `email`, com `Cache-Control: no-store` e histórico de requisição desabilitado. A atualização rejeita chaves extras; nenhum dado clínico é consultado ou gravado.
- Reutilizar o módulo de listagem Xano para abrir formulário editável com os campos cadastrais permitidos. Usar botões nativos do Streamlit e estilos/estrutura da referência; retirar “Observações de saúde” porque Recepcionista não pode alterar informação clínica.
- Testar os contratos sem rede com testes separados por rota em Python e JavaScript. Smoke Xano é opcional, limitado a 10 chamadas por 20 segundos e somente quando credenciais/ambiente estiverem explicitamente configurados.

## Risks / Trade-offs

- Dados cadastrais pessoais são devolvidos a equipe → exigir perfil no backend, enviar apenas o necessário, desabilitar histórico/cache e não registrar payloads.
- Atualização concorrente pode substituir uma edição recente → esta change não implementa controle de versão; enviar o estado integral validado e manter o escopo restrito a cadastro.
- A referência visual contém observações de saúde → omiti-las no formulário reduz fidelidade, mas respeita o limite de autorização clínica estabelecido no domínio.
- `cpf` pode estar nulo em cadastros antigos apesar da regra de unicidade → a leitura permite CPF vazio legado; salvar exige CPF válido conforme o contrato de cadastro.

## Migration Plan

Não há alteração de tabela ou migração de dados. Publicar as rotas Xano antes de habilitar a ação no Streamlit. Para rollback, remover as rotas e a ação de edição; dados existentes permanecem intactos.
