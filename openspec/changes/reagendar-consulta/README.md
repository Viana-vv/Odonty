# Reagendar Consulta — Issue #64

Implementação e validação Xano temporária concluídas para revisão. Nenhuma publicação em produção, integração à branch principal ou arquivamento da change foi realizada.

## Entrega

- Tabela aditiva `consulta_reagendamento` mantém vínculo entre Consulta original e nova, profissional responsável, justificativa e data.
- `POST /consultas/{id}/reagendamento` cancela a Consulta original, cria a nova, registra o vínculo e atualiza as Disponibilidades na mesma transação.
- `PATCH /disponibilidades/{id}` usa a trava compatível `agenda_controle` e relê/revalida o estado para rejeitar edições obsoletas durante uma reserva concorrente.
- O cliente REST usa o transporte comum. O fluxo não divide cancelamento e criação em chamadas separadas.
- A tela Streamlit isolada segue a composição de Nova Consulta do kit Sorriso Mais. A navegação permanece para integração posterior, conforme o escopo desta change.

## Testes locais

- Python: 56 testes passaram, incluindo os 20 AppTests da tela e testes de contrato/regressão.
- JavaScript: cinco testes passaram.
- `openspec validate reagendar-consulta --strict`: válido.
- `git diff --check`: passou.

Os testes de tela verificaram seletores, filtros, campos obrigatórios, lista vazia, permissões, sucesso, conflito, erros, sessão expirada e atualização da interface.

## Validação real em Xano temporário — 25/10/2026

O dry-run confirmou somente criação de objetos: 13 tabelas, uma função e sete rotas. O grupo `teste-reagendamento-64-70383d36` compilou e passou os cenários com dados fictícios, usando 74 requisições e intervalo mínimo medido de 3,188 s.

Foram verificados login e permissões (401/403), entradas inválidas (400), recurso inexistente (404), horário ocupado (409), reagendamento por Administrador e Recepcionista (201), preservação dos vínculos e relações anteriores, repetição (409) e rollback induzido sem alteração do snapshot.

Quatro disputas concorrentes reais mantiveram as duas operações sobrepostas no servidor: mesma Consulta, mesmo destino, mesmo Paciente e edição da Disponibilidade durante a reserva. Cada cenário resultou em uma operação 201 e outra 409. A limpeza confirmou a remoção do grupo, das 13 tabelas e da função temporários. O plano, bundle e relatório foram gravados fora do repositório em pasta temporária local; nenhum segredo foi registrado.

A primeira verificação read-only de 24/10 está documentada em [verificacao-xano-2026-10-24.md](verificacao-xano-2026-10-24.md). Ela registrou bloqueios que foram corrigidos e validados na execução temporária seguinte.

## Verificação visual integrada

A tela foi testada isoladamente com AppTests. A inspeção visual final em desktop e celular depende da integração da navegação e deve ser conferida após a integração temporária; não foi executada nesta worktree isolada.
