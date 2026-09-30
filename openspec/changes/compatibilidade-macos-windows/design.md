## Context

Ver [proposal.md](proposal.md) para a motivação e [specs/execucao-local-multiplataforma/spec.md](specs/execucao-local-multiplataforma/spec.md) para os comportamentos requeridos. O app já lê `XANO_API_BASE_URL` do ambiente e usa o mesmo fluxo Streamlit/Xano em todos os sistemas. O README concentra os passos de instalação e hoje utiliza PowerShell, caminhos `.venv/Scripts` e uma credencial local protegida por DPAPI.

## Goals / Non-Goals

**Goals:**

- Tornar o procedimento documentado executável em macOS e Windows com os mesmos requisitos de Python e dependências.
- Fornecer passos claros para que um integrante obtenha uma Conta de Acesso administrativa fictícia no Xano e valide o fluxo sem transportar credenciais locais.
- Manter a configuração específica da máquina fora do repositório.

**Non-Goals:**

- Mudar autenticação, autorização, endpoints ou tabelas do Xano.
- Criar usuário administrativo automaticamente, incluir senha de demonstração ou armazenar credenciais no app.
- Oferecer scripts ou instaladores separados por sistema operacional se comandos diretos no README forem suficientes.

## Decisions

### Usar comandos nativos por sistema no README

Documentar a criação do ambiente virtual e instalação em blocos para macOS (zsh/bash) e Windows PowerShell. No macOS, o interpretador e o Streamlit ficam em `.venv/bin`; no Windows, em `.venv/Scripts`. Usar `python3` no macOS e `py -3` no Windows para criar o ambiente, e chamar diretamente o interpretador virtual para não depender da ativação do shell. Isso evita diferenças de política de execução do PowerShell e de scripts de ativação.

Alternativa considerada: um script universal. Não adotar agora porque aumenta a manutenção e não há lógica de inicialização que justifique código auxiliar.

### Configurar variáveis somente no terminal local

Mostrar a configuração de `XANO_API_BASE_URL` e, quando aplicável, `XANO_HTTP_TIMEOUT_SECONDS` com a sintaxe própria do shell para aquela sessão. Indicar que `.env.example` é referência e não é carregado automaticamente. Não adicionar biblioteca de dotenv nem mudar `sorrisomais/config.py` nesta change.

Alternativa considerada: fazer o app carregar `.env`. Não adotar, pois altera comportamento de configuração e introduz dependência sem necessidade para iniciar o app.

### Substituir o caminho de credencial dependente de Windows por provisionamento no Xano

Documentar que cada integrante deve solicitar a um responsável uma Conta de Acesso administrativa fictícia já provisionada no Xano ou seguir o procedimento autorizado do workspace para criá-la. O arquivo DPAPI local não é portável e não deve ser copiado; senhas continuam digitadas somente no formulário de login e não entram no Git.

Alternativa considerada: guardar uma credencial compartilhada em `.env`. Rejeitada porque facilita vazamento e confunde configuração de conexão com credencial pessoal.

## Risks / Trade-offs

- Comandos podem divergir se a localização do executável Streamlit mudar em versões futuras das dependências → chamar o executável pelo ambiente virtual e validar os passos em ambos os sistemas quando disponíveis.
- Um integrante pode não ter permissão para criar contas no Xano → deixar explícita a dependência de provisionamento pelo responsável, sem conceder novas permissões.
- Documentar a credencial fictícia não torna a conta real segura para produção → reforçar que as contas e dados são exclusivamente demonstrativos e não clínicos.

## Migration Plan

Atualizar README, sem migração de dados ou endpoints. Após a revisão, remover a seção de extração via `Import-Clixml` e substituí-la por instrução de provisionamento no Xano. Rollback: restaurar a documentação anterior; não há alteração de estado externo.
