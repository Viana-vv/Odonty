## Why

O layout atual do Sorriso+ ainda não acompanha o kit de referência e mantém elementos de cabeçalho e rodapé que prejudicam a apresentação das telas. A change estabelece a navegação e a identidade visual das telas do kit em Streamlit, preservando os fluxos Xano que já funcionam e criando uma base testável para integrar, em etapas seguintes, as operações ainda sem contrato de API confirmado.

## What Changes

- Aplicar a identidade visual do kit às telas de login, visão geral, agenda, pacientes, profissionais, prontuários, procedimentos e formulários apresentados nas 15 referências.
- Remover o rodapé atual e o cabeçalho visual da aplicação, mantendo os controles do Streamlit necessários para funcionamento e acessibilidade.
- Organizar a navegação conforme o perfil autenticado e implementar uma camada demonstrativa por sessão, com dados exclusivamente fictícios e coerentes entre Paciente, Consulta, Profissional, Procedimento e Registro Clínico.
- Identificar permanentemente as telas e operações demonstrativas; não alegar persistência no Xano nem misturar dados demonstrativos com respostas reais da API.
- Preservar o login e as operações Xano já existentes fora do modo demonstrativo.
- Criar testes unitários para a navegação, apresentação por perfil, estados vazios, validações de interface e comportamento dos fluxos existentes afetados pelo layout.
- Registrar como dependência uma etapa OpenSpec posterior para integrar as operações demonstrativas ao Xano, após inspeção e aprovação do contrato real.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `interface-equipe`: ampliar a interface responsiva existente para abranger as telas e a navegação previstas no kit, remover o cabeçalho e rodapé visuais atuais, e oferecer demonstração fictícia claramente identificada sem alterar o modo Xano existente.

## Impact

- Streamlit: `app.py`, `sorrisomais/paginas_equipe.py`, módulos de tela e navegação que forem necessários.
- Estilos e recursos visuais em `assets/`.
- Testes unitários em `tests/`.
- Xano e API: os fluxos existentes devem permanecer compatíveis; esta change não altera o workspace nem inventa endpoints. Agenda, consultas, listagens e registros clínicos usam dados voláteis do modo demonstrativo até uma change própria integrar contratos auditados.
- Referências: `sorriso-mais-kit-recriacao/sorriso-mais-kit-recriacao/referencias-telas/` e especificação de telas do kit.
