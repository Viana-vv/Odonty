## Why

As instruções atuais de execução local e acesso demonstrativo usam comandos e credenciais protegidas exclusivamente pelo Windows. Isso impede que integrantes com macOS iniciem o Streamlit e reproduzam o fluxo administrativo com os mesmos passos documentados.

## What Changes

- Documentar instalação, configuração do Xano e inicialização do app com comandos equivalentes para macOS e Windows.
- Padronizar os caminhos do ambiente virtual e o carregamento das variáveis de ambiente nos dois sistemas.
- Documentar como preparar uma Conta de Acesso administrativa fictícia no Xano e validar o login sem compartilhar credenciais entre máquinas.
- Remover instruções que pressupõem disponibilidade de credencial DPAPI/Windows e explicar sua substituição multiplataforma.
- Manter autenticação, autorização e criação de Contas de Acesso no Xano; não adicionar credenciais de demonstração ao código ou ao repositório.

Fora do escopo: alterar endpoints ou permissões do Xano, criar automaticamente contas administrativas, suportar outros sistemas operacionais, distribuir instaladores ou alterar a interface do login.

## Capabilities

### New Capabilities

- `execucao-local-multiplataforma`: instruções reproduzíveis para configurar e iniciar a aplicação e validar o acesso da equipe no macOS e Windows.

### Modified Capabilities

Nenhuma. A change altera o processo local de desenvolvimento e sua documentação, sem mudar o comportamento funcional da autenticação ou as permissões existentes.

## Impact

README e documentação de desenvolvimento; possíveis scripts de conveniência para inicialização; verificação das dependências atuais. O backend Xano, os endpoints REST e o fluxo da interface permanecem sem alterações. Risco principal: divergência entre comandos documentados e versões de Python/dependências disponíveis em cada sistema, mitigada por passos explícitos e verificáveis.
