## Purpose

Permite que o Profissional registre a realização de cada Procedimento vinculado a uma Consulta, mantendo intactos os valores e a autoria do planejamento.

## ADDED Requirements

### Requirement: Consultar Procedimentos vinculados a uma Consulta

O sistema MUST permitir que um Profissional autenticado consulte os Procedimentos vinculados a uma Consulta sob seu próprio escopo. Cada item MUST apresentar sua situação e, quando realizado, a data e o Profissional responsável pela realização. A consulta MUST NOT alterar nem excluir vínculos existentes.

#### Scenario: Profissional consulta seus Procedimentos planejados

- **WHEN** um Profissional autenticado solicita os Procedimentos de uma Consulta que lhe pertence
- **THEN** o sistema retorna os vínculos existentes, incluindo dados do Procedimento, situação e autoria/data do planejamento, sem omitir situação planejada

#### Scenario: Consulta não existe ou está fora do escopo

- **WHEN** um Profissional solicita Procedimentos de uma Consulta inexistente ou pertencente a outro Profissional
- **THEN** o sistema retorna recurso não encontrado sem revelar dados da Consulta

#### Scenario: Perfil sem autorização tenta consultar Procedimentos

- **WHEN** uma Conta de Acesso que não é Profissional autenticado solicita os Procedimentos
- **THEN** o sistema nega o acesso sem retornar informações clínicas

### Requirement: Marcar Procedimento planejado como realizado

O sistema MUST permitir somente ao Profissional responsável pela Consulta alterar um vínculo existente de `planejado` para `realizado`. A transição MUST registrar o identificador do Profissional autenticado e a data/hora do servidor, preservar os campos de planejamento e manter o vínculo no histórico. O sistema MUST NOT permitir transição repetida ou exclusão do vínculo por esta operação.

#### Scenario: Realização autorizada

- **WHEN** o Profissional responsável pela Consulta marca um vínculo `planejado` como realizado
- **THEN** o sistema altera a situação para `realizado`, registra Profissional e data/hora da realização e preserva `profissional_id` e `criado_em` do planejamento

#### Scenario: Vínculo já realizado ou estado inválido

- **WHEN** a Conta de Acesso solicita realizar um vínculo que não está `planejado`
- **THEN** o sistema rejeita a alteração como conflito e mantém todos os dados existentes

#### Scenario: Profissional diferente tenta realizar Procedimento

- **WHEN** outro Profissional tenta marcar como realizado um vínculo de Consulta alheia
- **THEN** o sistema nega a operação sem alterar vínculo ou expor seus dados

#### Scenario: Vínculo inexistente

- **WHEN** o identificador do vínculo não pertence à Consulta informada
- **THEN** o sistema retorna recurso não encontrado sem alterar qualquer registro

### Requirement: Apresentar realização na tela profissional

A tela profissional MUST listar os Procedimentos de uma Consulta com indicação visual de situação. Deve oferecer ação para marcar somente Procedimentos planejados como realizados e exibir responsável e data nos realizados. Deve seguir cores, hierarquia, espaçamento e responsividade do kit Sorriso Mais.

#### Scenario: Consulta carrega com itens planejados e realizados

- **WHEN** Profissional abre a tela de Procedimentos da Consulta
- **THEN** a tela apresenta cada item e sua situação, disponibiliza ação apenas para itens planejados e apresenta responsável/data para os realizados

#### Scenario: Profissional conclui uma realização

- **WHEN** o Profissional confirma a ação em um item planejado e a API conclui a operação
- **THEN** a tela atualiza o item como realizado sem remover ou recriar o vínculo

#### Scenario: Falha ao consultar ou realizar

- **WHEN** a API retorna erro, indisponibilidade ou sessão expirada
- **THEN** a tela apresenta mensagem compreensível e segura, preserva os dados apresentados e não simula uma realização

#### Scenario: Lista sem Procedimentos

- **WHEN** uma Consulta não possui Procedimentos vinculados
- **THEN** a tela apresenta estado vazio sem fabricar itens
