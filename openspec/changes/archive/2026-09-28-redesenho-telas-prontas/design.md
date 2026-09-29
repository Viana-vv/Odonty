## Context

Ver `proposal.md` para motivação e `specs/interface-equipe/spec.md` para o contrato visual. O login em `app.py`, a página da equipe em `sorrisomais/paginas_equipe.py` e o formulário de Paciente em `sorrisomais/pagina_paciente.py` já funcionam; `assets/estilos.css` concentra a identidade visual atual. As referências de telas de módulos clínicos e operacionais não correspondem a funcionalidades disponíveis e não serão usadas para criar rotas novas.

## Goals / Non-Goals

**Goals:**

- Aplicar a identidade visual das referências 01, 02, 09 e 10 às telas funcionais.
- Incorporar o mascote `1000323602.jpg` encontrado na raiz.
- Preservar componentes Streamlit, estado, callbacks, autenticação e autorizações.
- Manter controles legíveis e navegáveis em celular, tablet, computador e teclado.

**Non-Goals:**

- Implementar páginas de Agenda, listagens, consultas, procedimentos ou prontuários.
- Simular dados ou colocar conteúdo fictício de paciente como se viesse do backend.
- Alterar endpoints, entidades, permissões, regras de cadastro ou credenciais.

## Decisions

1. **Reaproveitar os controles Streamlit atuais e aplicar a mudança em CSS e composição visual.** Isso preserva formulários, validação e testes de interação. Reconstruir os formulários em HTML próprio criaria controles duplicados e poderia quebrar acessibilidade e estado.

2. **Usar um início de equipe inspirado no painel geral, com ações existentes filtradas por perfil.** A tela poderá destacar o nome e o perfil da Conta de Acesso e oferecer os cadastros disponíveis. Não exibirá métricas, agenda, pacientes recentes ou links inativos, pois o app não tem essas consultas.

3. **Manter o login com e-mail e senha reais.** O print 01 contém seleção de perfil e senha demonstrativa; esses elementos não serão replicados porque a autenticação e o perfil são controlados pela Conta de Acesso no Xano.

4. **Apresentar os formulários como painéis focados, sem simular uma listagem no fundo.** Os prints 09 e 10 mostram modais sobre telas de lista que não existem. A composição vai aproveitar a hierarquia do modal e as referências de campos, mas a página seguirá autônoma.

5. **Adicionar o arquivo de imagem fornecido como asset estático e enquadrá-lo por CSS.** O arquivo encontrado tem extensão JPEG (`1000323602.jpg`) e inclui fundo branco e texto da marca; será usado sem alterar os pixels. A imagem `1000323602.png` não foi localizada.

6. **Centralizar regras visuais em `assets/estilos.css` e manter layout responsivo por breakpoints.** Reutilizar estilos atuais reduz mudanças nos fluxos e facilita rollback.

## Risks / Trade-offs

- A imagem tem fundo branco e texto de marca embutido → limitar o enquadramento ao espaço de apresentação e verificar contraste e legibilidade nas larguras suportadas.
- O Streamlit pode mudar a estrutura HTML interna entre versões → preferir classes/containers nomeados pelo app e seletores estáveis; validar nas versões instaladas.
- Referências mostram informações não disponíveis ao backend → não criar cartões ou atalhos para essas informações nesta change.

## Migration Plan

Copiar o asset fornecido para a pasta de recursos, ajustar os estilos e composições das telas existentes, e executar testes locais de login, cadastros, autorização e responsividade. Para reverter, restaurar os estilos/composições anteriores e retirar a referência ao novo asset; nenhuma migração de dados ou endpoint é necessária.
