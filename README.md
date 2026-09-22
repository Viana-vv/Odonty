# Sorriso+

MVP acadêmico para gerenciamento de uma clínica odontológica. A arquitetura definida utiliza Python e Streamlit na interface e Xano para autenticação, autorização e persistência via API REST. Implantação prevista em Render ou Railway.

## Estado atual

Esta cópia contém documentação de contexto e planejamento. Ainda não há aplicação Streamlit executável nem integração de login validada. O protótipo React/Vinext citado na solicitação, incluindo `app/page.tsx`, `app/globals.css` e sua configuração de hospedagem, não está presente nesta cópia. O usuário confirmou que esse protótipo não existe. A imagem 1000323602.jpg é a referência visual disponível.

## Documentação

- [Visão do projeto](docs/project-overview.md)
- [Modelo de domínio](docs/domain-model.md)
- [Instruções de trabalho](AGENTS.md)
- [Proposta de login](openspec/changes/login-streamlit-xano/proposal.md)
- [Decisões e dependências](openspec/changes/login-streamlit-xano/design.md)

## Configuração e execução

Os comandos de instalação e execução da aplicação, dependências Python e nomes das variáveis de ambiente serão documentados durante a implementação aprovada. Não existe `package.json` nesta cópia; `npm install` na raiz não instala a aplicação final.

O contrato de autenticação ainda precisa definir URLs, métodos, campos, respostas, identidade, perfis, expiração e logout. Endereços da API e configurações sensíveis utilizarão variáveis de ambiente. Credenciais administrativas do Xano CLI não são credenciais de login da aplicação.

## Verificação

A change está em preparação para revisão. Testes com respostas simuladas e testes reais contra o Xano deverão ser registrados separadamente. A integração real é condição de conclusão. Utilizar somente dados fictícios; o MVP não é destinado ao uso clínico real.

