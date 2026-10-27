## Why

O portal do Paciente já está implementado, mas falta confirmar que os contratos publicados no grupo Xano principal autenticam uma Conta de Acesso fictícia e retornam somente Consultas, Registros Clínicos liberados e Exames próprios. A validação precisa usar o Xano publicado real, sem criar APIs ou grupos temporários.

## What Changes

- Adicionar uma verificação de integração opt-in contra o grupo Xano publicado, sem tráfego de rede na suíte unitária padrão.
- Validar login/identidade/logout e as três leituras do portal com Conta de Acesso e dados exclusivamente fictícios já provisionados.
- Confirmar rejeição de acesso não autenticado e isolamento de dados próprios, sem modificar dados clínicos nem criar/alterar cadastros durante o teste.
- Documentar pré-requisitos e comandos sem persistir credenciais.

Fora do escopo: criar APIs, grupos temporários, contas ou registros em Xano; alterar autorização/contratos publicados; corrigir código do portal sem evidência de defeito.

## Capabilities

### New Capabilities
- `verificacao-autoatendimento-xano`: verificação opt-in dos contratos publicados usados pelo portal do Paciente.

### Modified Capabilities
- Nenhuma.

## Impact

Afeta somente testes de integração opt-in, documentação operacional e artefatos OpenSpec. Depende de `XANO_API_BASE_URL` e de credenciais de uma Conta de Acesso de Paciente fictícia provisionada no ambiente publicado. Nenhum segredo será registrado em arquivos ou logs.
