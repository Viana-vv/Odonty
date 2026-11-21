## Context

Veja `proposal.md` para a motivação. O Xano já possui a tabela `especialidade` com `nome`, `descricao` e `ativo`, e `GET /especialidades` fornece somente registros ativos ao cadastro administrativo de Profissional. Hoje não existe operação de criação na aplicação nem garantia de unicidade normalizada do nome.

A mudança atravessa Streamlit, cliente REST e Xano e exige uma pequena migração de dados para impedir duplicidades concorrentes sem perder a capitalização exibida ao usuário.

## Goals / Non-Goals

**Goals:**

- Criar Especialidades ativas por um contrato administrativo mínimo.
- Preservar um nome legível para exibição e uma chave normalizada para unicidade.
- Fazer a nova opção aparecer no cadastro de Profissional após atualização do cache.
- Manter autorização e validação efetivas no Xano.

**Non-Goals:**

- Editar, inativar, excluir ou descrever Especialidades.
- Alterar o relacionamento atual entre Profissional e Especialidade.
- Cadastrar múltiplas Especialidades em um único envio.

## Decisions

### Endpoint dedicado e corpo estrito

Será criado `POST /especialidades`, autenticado por `conta_acesso`, com corpo estrito contendo apenas `nome`. O Xano validará a sessão, reconsultará o solicitante e exigirá Conta de Acesso ativa com perfil Administrador. A Especialidade será criada com `ativo: true`; identificador, situação, descrição ou campos extras enviados pelo cliente causarão rejeição.

O uso da mesma coleção de `GET /especialidades` mantém o contrato REST previsível. A alternativa de incluir criação dentro de `POST /profissionais` foi descartada porque misturaria dois cadastros, dificultaria reutilização e aumentaria o risco de registros parciais.

### Nome de exibição separado da chave de unicidade

O campo `nome` armazenará a forma de exibição após aparar e consolidar espaços. Um novo campo interno `nome_normalizado` armazenará o mesmo conteúdo em minúsculas e terá índice único. O endpoint preencherá os dois campos na mesma gravação.

Um índice único direto em `nome` foi descartado porque permitiria duplicidades apenas por diferença de caixa em bancos com comparação sensível, ou exigiria guardar o texto de exibição todo em minúsculas. A chave separada preserva a apresentação e protege envios concorrentes.

Antes de tornar o índice único obrigatório, os registros existentes serão auditados, normalizados e preenchidos. Duplicidades encontradas deverão ser resolvidas preservando uma Especialidade canônica e ajustando referências antes de publicar a rota. Nenhuma Especialidade referenciada será apagada automaticamente.

### Formulário administrativo e cache

O painel mostrará “Cadastrar especialidade” somente para Administrador, junto às ações administrativas de cadastro. A ação abrirá um modal responsivo com um único campo de nome e estado próprio, separado do cadastro de Profissional.

O cliente enviará um único `POST`, validará a resposta `201` com `id`, `nome` e `ativo: true` e não repetirá automaticamente resultados incertos. Depois de sucesso confirmado, a interface invalidará o namespace de cache `especialidades`. Ao abrir ou atualizar o cadastro de Profissional, o `GET /especialidades` buscará novamente as opções ativas.

### Verificação por contrato e interface

O novo `POST` terá arquivos unitários separados em Python e JavaScript, sem rede real, cobrindo rota, corpo estrito, autorização, normalização, conflito e resposta. Testes de interface cobrirão visibilidade por perfil, validação, envio único, invalidação de cache, sucesso e falhas seguras. O `GET /especialidades` existente permanecerá coberto por seus testes atuais.

## Risks / Trade-offs

- [Dados existentes podem conter nomes equivalentes] → Auditar e resolver colisões antes de aplicar a restrição única, preservando referências de Profissionais.
- [A resposta pode se perder depois da gravação] → Não repetir o `POST`; orientar a atualização da lista, que confirmará a existência pelo nome normalizado.
- [O cache pode esconder a nova opção] → Invalidar `especialidades` somente após sucesso confirmado e manter ação explícita de atualização.
- [Criação manual no Xano pode omitir a chave normalizada] → Documentar o endpoint como caminho suportado e tornar `nome_normalizado` obrigatório após o backfill.
- [A árvore atual contém mudanças não relacionadas] → A implementação deverá alterar somente os arquivos desta change e preservar as alterações existentes.

## Migration Plan

1. Auditar Especialidades existentes e mapear colisões por nome aparado, espaços consolidados e minúsculas.
2. Resolver colisões com decisão explícita sobre o registro canônico e atualizar referências sem excluir histórico.
3. Adicionar e preencher `nome_normalizado`, torná-lo obrigatório e criar o índice único.
4. Publicar `POST /especialidades` e validar autorização, normalização e concorrência com dados fictícios.
5. Publicar o cliente e o formulário Streamlit, então executar os testes Python, JavaScript e de interface sem rede.
6. Em rollback da interface, ocultar a ação; em rollback do endpoint, despublicar a rota. Não remover automaticamente o campo, o índice nem Especialidades já criadas.
