## 1. Exploração e recursos

- [x] 1.1 Registrar inventário de todas as telas documentadas e seus ícones, verificável em docs/icones-interface.md.
- [x] 1.2 Revisar fontes, scripts, dependências e SVGs externos e incorporar somente vetores estáticos fixados com licença e hashes; 11 testes positivos e negativos aprovados.

## 2. Implementação

- [x] 2.1 Criar renderização compartilhada dos ícones e estilos para controles nativos preservando rótulos e callbacks; testes de acessibilidade e segurança aprovados.
- [x] 2.2 Trocar glifos e SVGs próprios em painéis, menus, Agenda, listagens, formulários e demonstração; inventário documentado e busca sem os símbolos substituídos.
- [x] 2.3 Aplicar iconografia aos controles comuns de equipe e Paciente preservando mascotes e imagens; diff sem mudanças nas imagens e navegador aprovado em desktop e celular.

## 3. Verificação e entrega

- [x] 3.1 Executar regressão Python e capturas automatizadas das telas com dados fictícios: 255 testes aprovados e 30 composições em duas resoluções, com ações, nomes, contraste, proporções e bloqueio de recursos externos no roteiro adicional.
- [x] 3.2 Atualizar documentação e validar OpenSpec, revisar diff, commitar e enviar branch feat/icones-regen-sorrisoplus vinculada à Issue #125; PR #126 aberta sem merge.
