## Context

Veja `proposal.md` para a motivação. A tabela `conta_acesso` já autentica os perfis Administrador, Recepcionista, Profissional e Paciente, possui e-mail único e armazena a senha em campo próprio do Xano. A aplicação já possui o padrão de cadastro administrativo de Profissional, mas não há contrato de criação de uma Conta de Acesso exclusivamente administrativa.

O fluxo atravessa a interface Streamlit, o cliente REST e o Xano. Por envolver criação de credencial e atribuição de perfil, a autorização e a fixação do privilégio precisam permanecer no backend.

## Goals / Non-Goals

**Goals:**

- Reutilizar a Conta de Acesso existente sem introduzir uma entidade Recepcionista separada.
- Criar uma operação mínima, estrita e exclusiva do Administrador.
- Preservar a sessão do Administrador e proteger a senha durante todo o fluxo.
- Manter o formulário isolado do cadastro de Paciente e de Profissional.

**Non-Goals:**

- Criar ou promover Contas de Acesso para Administrador.
- Editar perfis, situação ou credenciais depois do cadastro.
- Associar Recepcionista a Paciente, Profissional ou dados clínicos.

## Decisions

### Endpoint dedicado com privilégio fixo

Será criado `POST /contas-acesso/recepcionistas`, autenticado por `conta_acesso`. O corpo aceitará estritamente `nome`, `email` e `senha`; perfil, situação e identificador enviados pelo cliente causarão rejeição. O Xano gravará `perfis: ["recepcionista"]` e `situacao: "ativo"` sem usar valores de privilégio vindos do Streamlit.

Um `POST /contas-acesso` genérico foi descartado porque exigiria aceitar ou inferir vários tipos de conta e ampliaria a superfície de elevação de privilégio.

### Autorização e validação no Xano

O endpoint executará a validação de sessão existente e reconsultará a Conta de Acesso solicitante, exigindo situação ativa e perfil Administrador. Nome, e-mail e senha serão validados novamente no Xano. O e-mail será aparado e convertido para minúsculas antes da consulta e gravação; o índice único já existente continuará sendo a proteção final contra concorrência.

Conflitos de e-mail retornarão `409`, dados inválidos `400`, ausência de autenticação `401`, falta de permissão `403` e falha não confirmada `503`, sempre com corpo seguro. A resposta `201` conterá somente a projeção pública da nova Conta de Acesso.

### Formulário administrativo isolado

O painel mostrará “Cadastrar recepcionista” somente para Administrador, junto às ações de cadastro já existentes. A ação abrirá um modal responsivo seguindo o padrão visual do cadastro de Profissional. Chaves de estado próprias impedirão colisão com outros formulários e o envio ficará bloqueado enquanto estiver em processamento.

A confirmação da senha existirá somente na interface e não será enviada ao Xano. Senha e confirmação serão removidas após qualquer resultado ou ao fechar o modal. O cliente validará a estrutura mínima da resposta e não repetirá automaticamente um `POST` cujo resultado seja incerto.

Após sucesso, o cache da listagem `contas-acesso` será invalidado para que uma futura consulta reflita a conta criada. A sessão atual permanecerá vinculada ao Administrador.

### Verificação por contrato e interface

O novo `POST` terá arquivos unitários separados em Python e JavaScript, sem rede real, cobrindo rota, autorização, corpo estrito, resposta mínima e ausência de credenciais. Testes de interface cobrirão visibilidade por perfil, validações, envio único, sucesso e falhas seguras.

## Risks / Trade-offs

- [Uma rota de criação de credencial pode elevar privilégios] → O perfil e a situação serão constantes no Xano e campos extras serão rejeitados.
- [A resposta pode se perder depois da gravação] → A interface não repetirá o envio e orientará conferir a listagem antes de tentar novamente; a unicidade do e-mail evita uma segunda conta.
- [A senha pode permanecer no estado do Streamlit] → As chaves de senha serão apagadas em sucesso, erro e fechamento do modal, sem registro de payloads.
- [A árvore atual contém mudanças não relacionadas] → A implementação deverá alterar somente os arquivos desta change e preservar as alterações existentes.

## Migration Plan

1. Publicar o endpoint no Xano e validar autorização, duplicidade e projeção da resposta com dados fictícios.
2. Publicar o cliente e o formulário Streamlit após o endpoint estar disponível.
3. Executar os testes unitários Python, JavaScript e de interface sem rede.
4. Em rollback, remover a ação da interface e despublicar o endpoint; Contas de Acesso já criadas permanecem preservadas e podem ser inativadas pelo processo administrativo existente.
