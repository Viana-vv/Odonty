# Design

## Context

Consulte `proposal.md` para a motivação e `specs/gestao-disponibilidades/spec.md` para os comportamentos. O cliente Xano já possui criação de Disponibilidade e a API lista Profissionais; a Agenda ainda não oferece formulário para essa operação. O Xano deve continuar sendo a fonte de autorização, validação de intervalo e persistência.

## Goals / Non-Goals

**Goals:**
- Conectar um formulário simples na Agenda aos contratos existentes.
- Tornar o resultado do cadastro observável e atualizar os dados da Agenda após sucesso.
- Tratar respostas vazias, falhas e rejeições sem indicar sucesso incorretamente.

**Non-Goals:**
- Criar recorrência, edição ou bloqueio de Disponibilidades.
- Mudar o modelo de dados ou substituir as regras e permissões do Xano.

## Decisions

- Reutilizar `ClienteXano.criar_disponibilidade` e a API de opções de agendamento, evitando um novo contrato REST. Alternativa considerada: criar endpoints específicos para o formulário; isso duplicaria operações já disponíveis.
- Colocar a ação na tela da Agenda junto às ações de agendamento e manter o formulário em um intervalo por envio. Isso acompanha a unidade aceita pela API existente e facilita corrigir conflitos.
- Converter a data e os horários informados para o formato esperado pelo cliente existente, sem calcular disponibilidade ou autorizar a operação no frontend. O Xano segue validando intervalo futuro, profissional e conflitos.
- Atualizar ou recarregar a Agenda somente depois da confirmação da API. Em falhas, preservar os valores do formulário quando possível e apresentar mensagem compreensível, sem expor detalhes técnicos.
- Antes de integrar, verificar a execução real/compilação do endpoint Xano existente e os perfis que ele autoriza. Corrigir apenas defeitos diretamente impeditivos deste cadastro, mantendo a matriz prevista na proposta.

## Risks / Trade-offs

- O contrato Xano existente pode ter defeito de execução ou resposta incompatível com o cliente → verificar contrato e corrigir o mínimo necessário antes de habilitar a ação.
- A lista de opções pode estar vazia ou indisponível → distinguir ausência de Profissionais ativos de falha ao carregar opções e impedir envio sem seleção válida.
- Uma sessão pode expirar entre abrir o formulário e salvar → tratar rejeição de autenticação/autorização conforme o fluxo existente e não alegar sucesso.

## Migration Plan

Não há migração de dados prevista. Publicar qualquer correção necessária do endpoint existente antes da interface; depois publicar o app. Para reverter, retirar a ação/formulário do Streamlit; os dados de Disponibilidade já persistidos continuam válidos e não devem ser apagados.
