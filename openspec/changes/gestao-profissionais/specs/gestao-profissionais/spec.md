## Purpose

Permitir consulta administrativa consistente dos Profissionais e alteração segura de sua situação sem perder referências e registros históricos associados.

## ADDED Requirements

### Requirement: Consultar os dados cadastrais dos Profissionais
O sistema SHALL permitir que Administrador e Recepcionista consultem Profissionais ativos e inativos, apresentando somente identificador, nome, CRO, especialidade, e-mail profissional, telefone e situação. Campos opcionais sem valor devem ser apresentados como não informado. A consulta não deve expor CPF, credenciais, dados de Conta de Acesso ou informações clínicas.

#### Scenario: Administrador ou Recepcionista consulta Profissionais
- **WHEN** uma Conta de Acesso autorizada consulta a listagem
- **THEN** o Xano retorna os dados cadastrais permitidos de Profissionais ativos e inativos, ordenados pelo nome

#### Scenario: Lista vazia
- **WHEN** não existem Profissionais cadastrados
- **THEN** a interface informa que não há Profissionais para exibir

#### Scenario: Falha de consulta
- **WHEN** a API falha ou a sessão expirou
- **THEN** a interface apresenta mensagem compreensível e não apresenta resultados antigos como atuais

#### Scenario: Conta sem permissão
- **WHEN** uma Conta de Acesso sem perfil Administrador ou Recepcionista consulta a rota
- **THEN** o Xano responde com acesso negado e não retorna dados

### Requirement: Administrador altera situação sem apagar histórico
O sistema SHALL permitir que somente Administrador ativo com sessão válida altere a situação de um Profissional existente entre ativo e inativo. A alteração não deve excluir nem modificar Consultas, disponibilidades ou outras referências históricas. Profissional inativo não pode receber novos agendamentos.

#### Scenario: Inativação confirmada
- **WHEN** Administrador solicita situação inativo para Profissional existente
- **THEN** o Xano atualiza a situação, preserva os dados e relacionamentos históricos, e retorna a situação confirmada

#### Scenario: Reativação confirmada
- **WHEN** Administrador solicita situação ativo para Profissional existente
- **THEN** o Xano atualiza a situação e permite que as regras existentes de agenda considerem o Profissional ativo

#### Scenario: Recepcionista tenta alterar situação
- **WHEN** Recepcionista chama diretamente a rota de alteração
- **THEN** o Xano responde com acesso negado e não altera o Profissional

#### Scenario: Profissional inexistente ou situação inválida
- **WHEN** a alteração referencia identificador inexistente ou situação diferente de ativo/inativo
- **THEN** o Xano rejeita a operação sem alterar dados

#### Scenario: Inativação não apaga consultas históricas
- **WHEN** um Profissional com Consultas existentes é inativado
- **THEN** as Consultas permanecem vinculadas e disponíveis no histórico

### Requirement: Interface respeita o perfil e é responsiva
A área Profissionais SHALL exibir os dados retornados pelo Xano em cartões responsivos. Administrador pode acionar ativação/inativação e confirmar a ação; Recepcionista visualiza os mesmos dados sem controles de alteração.

#### Scenario: Administrador gerencia situação
- **WHEN** Administrador confirma ativação ou inativação
- **THEN** a interface envia a alteração, atualiza a lista após sucesso e apresenta erro sem ocultar a situação atual confirmada pela API

#### Scenario: Recepcionista consulta somente
- **WHEN** Recepcionista abre a área Profissionais
- **THEN** vê os cartões sem ações para alterar situação

#### Scenario: Exibição em telas estreitas
- **WHEN** os cartões são exibidos em celular ou tablet
- **THEN** os dados e controles permanecem legíveis, alcançáveis e sem exigir rolagem horizontal
