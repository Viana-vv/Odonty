## Why

O formulário Nova Consulta já usa os contratos corretos, porém sua apresentação pode comunicar melhor a sequência de agendamento e se aproximar da referência 08 do kit Sorriso Mais. Um refinamento visual focado deve facilitar a leitura sem introduzir novos campos, rotas ou etapas.

## What Changes

- Reorganizar visualmente os campos atuais para destacar Paciente, Data e Profissional, depois Horário e Procedimentos, mantendo Observações e as ações no encerramento do formulário.
- Ajustar hierarquia, espaçamento e apresentação responsiva conforme o kit Sorriso Mais.
- Preservar mensagens de sucesso, erro, vazio, validações, perfis e tratamento de conflito atuais.

Fora do escopo: alterar Agenda, contratos, payloads, regras no Xano, adicionar campos ou novas funcionalidades.

## Capabilities

### New Capabilities
Nenhuma.

### Modified Capabilities
- `interface-equipe`: detalhar a apresentação responsiva e a preservação do formulário Nova Consulta existente.

## Impact

- Interface: `sorrisomais/pagina_nova_consulta_xano.py`.
- Especificação visual: referência `08-nova-consulta.png` do kit.
- Testes de interface sem rede e contratos existentes de GET `/agenda/opcoes`, GET `/disponibilidades` e POST `/consultas`.
- Nenhuma mudança nos endpoints, permissões ou dados do Xano.
