## Why

As telas de Exames, Reagendamento e Procedimentos da Consulta já possuem clientes e interfaces próprios, mas não estão alcançáveis pelo fluxo autenticado da equipe. A navegação deve expor cada capacidade ao perfil autorizado e fornecer a Consulta selecionada quando a tela de Procedimentos for aberta.

## What Changes

- Registrar Exames e Reagendamento como áreas roteáveis da equipe, com visibilidade conforme os perfis definidos nos contratos existentes.
- Disponibilizar Procedimentos da Consulta no contexto de uma Consulta selecionada pelo Profissional, mantendo distinto o catálogo administrativo de Procedimentos.
- Tratar rota direta, contexto ausente ou inválido e módulo indisponível com retorno seguro a uma área válida e mensagem compreensível.
- Acrescentar testes de navegação e integração entre os pontos de entrada e as interfaces existentes.

Fora do escopo: portal de Paciente da Issue #84, mudanças nos contratos ou permissões Xano, alterações nos clientes/telas existentes e mudanças no catálogo de Procedimentos.

## Capabilities

### New Capabilities

- `fluxo-telas-equipe`: integração das telas clínicas existentes na navegação autenticada da equipe.

### Modified Capabilities

- Nenhuma.

## Impact

- Arquivos da aplicação: `sorrisomais/navegacao.py` e `sorrisomais/paginas_equipe.py`.
- Testes: testes unitários de roteamento e interface sem chamadas reais de rede.
- Dependências: clientes e telas existentes de Exames, Reagendamento e Procedimentos da Consulta.
- Segurança: a navegação limita apresentação por perfil; Xano continua responsável pela autorização efetiva. A tela de Procedimentos só recebe Consulta escolhida no fluxo autenticado do Profissional.
- Referência visual: pontos de entrada seguem a hierarquia e composição do kit Sorriso Mais já usado no menu, agenda e painel da equipe.
