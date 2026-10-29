## Context

Consulte `proposal.md` e `specs/interface-equipe/spec.md`. A composição do painel usa colunas de Streamlit para Agenda e Acesso rápido. Em 768 px, a captura reproduzível mantém essa linha em `row`, e o rótulo do botão do cabeçalho fica truncado. A regra responsiva existente em `assets/estilos.css` seleciona o bloco horizontal como filho direto do contêiner, mas o DOM do Streamlit insere um `stLayoutWrapper` intermediário.

## Goals / Non-Goals

**Goals:**

- Fazer a regra responsiva existente alcançar somente a linha principal do painel Profissional em tablets.
- Preservar a linha lado a lado em desktop e a composição vertical funcional em celular.
- Manter conteúdo e ações do painel sem alterações.

**Non-Goals:**

- Alterar componentes, dados, APIs, permissões, outras telas ou o funcionamento dos atalhos.
- Refatorar o CSS global ou mudar a responsividade de outras áreas.

## Decisions

- Corrigir o seletor CSS do painel para atravessar o `stLayoutWrapper` que envolve o primeiro `stHorizontalBlock`, mantendo o escopo em `st-key-painel-profissional-conteudo` e o breakpoint existente de 900 px. Isso permite que a regra planejada para empilhar Agenda e Atalhos seja aplicada no DOM real. Alternativa: mudar a proporção das colunas ou reduzir fontes; descartada porque mantém o empilhamento pretendido sem reduzir legibilidade.
- Verificar por teste que o seletor escopado permanece no CSS e por captura de navegador nas larguras 360, 390, 768 e 1440 px que o tablet empilha, o desktop mantém colunas, o rótulo não é cortado e a página não ganha rolagem horizontal.

## Risks / Trade-offs

- Uma mudança futura no DOM do Streamlit pode alterar o wrapper → manter teste do seletor e repetir a inspeção visual nos quatro tamanhos.

## Migration Plan

Não há migração. Reverter consiste em restaurar o seletor anterior.
