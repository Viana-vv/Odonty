## Purpose

Define um processo local reproduzível para que integrantes usem o Sorriso+ e validem o acesso administrativo em macOS e Windows, sem depender de credenciais ou recursos exclusivos de uma máquina.

## ADDED Requirements

### Requirement: Instalação e inicialização multiplataforma
O projeto SHALL documentar comandos completos para criar um ambiente Python isolado, instalar as dependências, configurar `XANO_API_BASE_URL` e iniciar o Streamlit em macOS e Windows. Os comandos SHALL usar o interpretador do ambiente virtual e SHALL apontar para a mesma aplicação e endereço local.

#### Scenario: Integrante inicia no macOS
- **WHEN** o integrante segue as instruções a partir de um clone limpo em macOS com Python compatível instalado
- **THEN** consegue instalar as dependências, configurar a URL HTTPS do grupo Xano e iniciar a aplicação no Streamlit local

#### Scenario: Integrante inicia no Windows
- **WHEN** o integrante segue as instruções a partir de um clone limpo em Windows com Python compatível instalado
- **THEN** consegue instalar as dependências, configurar a URL HTTPS do grupo Xano e iniciar a aplicação no Streamlit local

#### Scenario: Configuração obrigatória ausente ou inválida
- **WHEN** o aplicativo inicia sem `XANO_API_BASE_URL` válida
- **THEN** apresenta a orientação de configuração já prevista e não habilita o envio do login

### Requirement: Acesso administrativo fictício independente de máquina
As instruções SHALL explicar que o login administrativo utiliza uma Conta de Acesso fictícia ativa criada e autorizada no Xano. A validação de acesso SHALL funcionar em macOS e Windows sem depender de arquivo de credenciais específico de sistema operacional, e credenciais SHALL permanecer fora do código e do Git.

#### Scenario: Administrador fictício entra em macOS ou Windows
- **WHEN** a pessoa configura a URL do Xano e informa as credenciais de uma Conta de Acesso administrativa fictícia ativa
- **THEN** a aplicação valida o login e apresenta as ações permitidas pelo backend para Administrador

#### Scenario: Repositório é clonado em outra máquina
- **WHEN** uma pessoa clona o repositório sem possuir os arquivos locais de credenciais demonstrativas de outra máquina
- **THEN** pode configurar uma Conta de Acesso fictícia no Xano por procedimento documentado e testar o login sem importar artefatos específicos de Windows ou compartilhar segredos no repositório
