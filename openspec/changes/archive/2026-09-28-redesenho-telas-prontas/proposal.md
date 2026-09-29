## Why

As telas atuais do Sorriso+ já permitem entrar na Conta de Acesso, identificar a equipe e cadastrar Pacientes e Profissionais, mas ainda não seguem a identidade visual mostrada nas referências do projeto. O redesenho aproxima essas telas dos prints e incorpora o mascote fornecido, preservando os fluxos que já funcionam.

## What Changes

- Atualizar o visual do login, da página inicial da equipe e dos formulários de cadastro de Paciente e Profissional conforme as referências correspondentes.
- Incorporar o mascote fornecido ao layout, com apresentação adequada em telas grandes e celulares.
- Manter autenticação, autorização, validações, integração REST, navegação e mensagens atuais.
- Restringir navegação e ações às funcionalidades que já existem; não apresentar módulos não implementados como disponíveis.
- Usar o arquivo `1000323602.jpg`, encontrado na raiz do projeto. O arquivo `1000323602.png` citado pelo grupo não foi localizado.

## Capabilities

### New Capabilities

- `interface-equipe`: apresentação visual, responsividade e acessibilidade das telas já disponíveis para a equipe.

### Modified Capabilities

Nenhuma. O contrato funcional, as permissões e as regras de cadastro permanecem iguais.

## Impact

- Frontend Streamlit: `app.py`, `sorrisomais/paginas_equipe.py` e `sorrisomais/pagina_paciente.py`.
- Estilos em `assets/estilos.css` e incorporação do mascote existente.
- Testes de interface e documentação visual/execução, sem alterações em endpoints, tabelas ou regras do Xano.
- Referências visuais: `sorriso-mais-prints/referencias-telas/01-login.png`, `02-visao-geral.png`, `09-novo-paciente.png` e `10-novo-profissional.png`.

## Fora do escopo

- Criar Agenda, listagem de Pacientes, listagem de Profissionais, Prontuários, Procedimentos, Consultas ou outras telas que ainda não possuem fluxo implementado.
- Copiar credenciais demonstrativas, dados de pessoas ou ações fictícias dos prints.
- Alterar autenticação, permissões, API, modelo de dados ou comportamento dos formulários.
