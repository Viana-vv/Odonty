## Context

Os dois formulários são renderizados nos modais existentes da equipe Streamlit e compartilham os estilos de `assets/estilos.css`. As referências definem uma composição comum de modal, título, descrição, campos alinhados e ações no rodapé. Os contratos já especificados para Paciente e Profissional têm conjuntos de campos distintos das imagens.

## Goals / Non-Goals

**Goals:**
- Refinar apresentação e disposição dos campos nos modais existentes.
- Aproveitar as classes e os tokens visuais compartilhados do kit Sorriso Mais.
- Manter os fluxos de estado e submissão atuais.

**Non-Goals:**
- Alterar campos, validações, permissões, APIs REST, persistência ou regras de domínio.
- Implementar campos visíveis nas referências que não existam nos contratos atuais.
- Alterar os formulários da demonstração ou outras páginas.

## Decisions

- Manter os contêineres de modal e suas chaves CSS atuais. A alternativa de trocar por outro mecanismo de diálogo poderia mudar interação, foco e estado de navegação sem necessidade para o refinamento visual.
- Ajustar apenas a hierarquia e a disposição dos campos existentes dentro dos formulários administrativos, usando a ordem e o agrupamento visual da referência sempre que compatíveis com os campos contratados.
- Centralizar espaçamento, dimensões e adaptações de largura no CSS compartilhado e manter a rolagem do modal em telas baixas ou estreitas. Não adicionar dependências ou estilos inline.
- Preservar chamadas atuais de cadastro no cliente Xano, estados de sessão, tratamento de erros e verificação de acesso.

## Risks / Trade-offs

- Seletores CSS baseados em estrutura do Streamlit podem mudar entre versões → limitar os ajustes às classes de modal já usadas e confirmar o resultado na verificação de interface disponível.
- Os campos do sistema não coincidem integralmente com as imagens → manter os campos contratados e aplicar a identidade visual sem inventar dados ou remover campos funcionais.

## Migration Plan

Não há migração ou alteração de implantação: os ajustes são de interface e estilos locais.
