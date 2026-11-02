## Why

Os ícones atuais misturam glifos, desenhos próprios e Material Symbols. O usuário solicitou unificá-los com Regen Icons após revisão de segurança, preservando imagens, mascotes, marca, layout e funcionalidades.

## What Changes

- Revisar o repositório externo em revisão fixa e incorporar somente SVGs estáticos necessários, com licença e procedência.
- Substituir ícones de navegação, indicadores, ações e controles nas telas existentes dos perfis Administrador, Recepcionista, Profissional e Paciente, incluindo demonstração.
- Preservar rótulos acessíveis, interação, permissões, dimensões e responsividade existentes.
- Documentar o inventário das telas e o resultado e limites da revisão de segurança.
- Não alterar imagens, mascotes, logo, backend, autenticação, dados ou contratos REST; não executar gerador externo nem adicionar dependências JavaScript.

## Capabilities

### New Capabilities

- `icones-interface`: iconografia vetorial consistente, local e acessível em todas as interfaces existentes.

### Modified Capabilities

Nenhuma regra funcional ou de domínio alterada.

## Impact

Frontend Streamlit, estilos, SVGs locais, testes visuais e documentação. Sem impacto no Xano. Riscos: SVG ativo, perda de nomes acessíveis e contraste em estados de botões; mitigar com validação restrita dos vetores, rótulos preservados e conferência em navegador.
