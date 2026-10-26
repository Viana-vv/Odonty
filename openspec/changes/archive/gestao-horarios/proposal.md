## Why

A Agenda atualmente permite cadastrar uma Disponibilidade e selecionar horários livres para consultas, mas não permite conferir ou manter os horários existentes. A equipe precisa ajustar intervalos e controlar bloqueios sem sair da Agenda.

## What Changes

- Exibir, na Agenda, as Disponibilidades futuras do dia selecionado, com Profissional, intervalo e situação.
- Permitir editar o intervalo e bloquear ou desbloquear uma Disponibilidade livre, respeitando o escopo do Profissional e os perfis autorizados.
- Manter validação de conflitos, autorização e rejeição de horários reservados, passados ou sobrepostos no Xano.
- Estender o GET existente para incluir Disponibilidades bloqueadas necessárias ao desbloqueio.

Fora do escopo: criar tela independente, cadastro recorrente, exclusão de Disponibilidades e alteração de consultas.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `interface-equipe`: complementar a Agenda com leitura e manutenção de Disponibilidades.

## Impact

- Interface em `sorrisomais/paginas_equipe.py` e cliente já existente `ClienteXano`.
- Rotas existentes `GET /disponibilidades` e `PATCH /disponibilidades/{id}`; sem novo contrato.
- Export Xano do GET inclui apenas Disponibilidades futuras livres ou bloqueadas. PATCH existente aplica autorização, escopo, validação e conflito.
- Sem migração de dados ou alteração de tabelas.
