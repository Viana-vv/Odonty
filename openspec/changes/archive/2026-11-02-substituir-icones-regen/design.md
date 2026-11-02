## Context

Exploração: Streamlit renderiza ícones próprios em controles e glifos/SVGs nos indicadores. Os testes usam nomes e chaves dos botões. O pedido aprova a execução completa nesta branch e uma PR sem merge. A motivação e os limites estão na proposta.

## Goals / Non-Goals

Manter a interface e os contratos funcionais enquanto se troca apenas a iconografia. Não migrar frontend, executar gerador externo, alterar imagens ou acessar dados reais. Nenhum endpoint ou modelo de dados é afetado.

## Decisions

- Copiar somente SVGs outline revisados do commit `64c0e165c3ce6d5c9d7329acf5762306f86d6b1d`, mantendo licença MIT, procedência e hashes. Usar recursos locais evita instalação de pacotes e tráfego gráfico externo.
- Centralizar SVG inline decorativo e máscaras CSS com `currentColor` em módulo de ícones. Máscaras nos controles nativos preservam nomes, chaves, callbacks e semântica de teclado, sem inserir imagens rasterizadas em botões.
- Substituir glifos de indicadores e desenhos próprios por vetores da família. O conjunto não possui dente: usar `tool` para Procedimentos e `clipboard-check` para atendimentos, sem criar um desenho externo à família.
- Estilizar controles comuns (alertas, busca, seleção, expansão, calendário e senha) sem substituir a implementação dos widgets. Documentar qualquer limite concreto de controles internos do framework na verificação.
- A documentação atual de telas é inventariada por um agente em paralelo à revisão externa. A implementação começa após concluir exploração e revisar coerência dos artefatos, dentro da autorização explícita do usuário.

## Risks / Trade-offs

- SVG ativo → lista restrita de elementos e atributos, rejeição de eventos e referências externas e testes negativos.
- Seletores internos de Streamlit podem mudar → concentrar em um módulo e verificar navegador e testes na versão instalada.
- Contraste e ícones isolados → herdar cor dos controles, manter nomes acessíveis e testar estados ativo, desabilitado e móvel.
- Revisão estática não prova ausência absoluta de malware → registrar alcance e revisão fixa; não executar dependências ou scripts externos.

## Migration Plan

Entregar frontend, SVGs, licença, inventário e verificações juntos na PR. Reversão pelo commit da mudança, sem migração de dados. Não fazer merge.
