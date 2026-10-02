## Why

O cadastro de Profissional já possui interface, cliente REST e endpoints versionados, mas a change arquivada deixou tarefas de verificação sem uma conclusão coerente. Esta retomada limita-se a conferir o código e executar testes unitários locais, sem depender de acesso ao Xano.

## What Changes

- Conferir os contratos REST e o fluxo do cadastro no código local.
- Executar somente testes unitários Python e JavaScript, sem requisições reais à rede.
- Corrigir divergências locais comprovadas em relação aos requisitos existentes.
- Registrar no README os comandos, resultados simulados e limites das verificações.

Fora do escopo: testes ou alterações remotas no Xano, testes de navegador, novos perfis, campos, endpoints ou regras de domínio; alterações nas funcionalidades de Paciente, Agenda ou Prontuário; uso de dados reais.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

Nenhuma. A mudança verifica e, se necessário, corrige a implementação para cumprir os requisitos existentes de `cadastro-profissional` e `acesso-autenticado`, sem alterar seus contratos.

## Impact

Cliente REST e telas Streamlit existentes, testes unitários de contrato em Python e JavaScript, documentação de execução e registros OpenSpec. Nenhuma chamada ou alteração remota ao Xano faz parte desta change.
