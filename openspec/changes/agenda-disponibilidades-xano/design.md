## Context

Os arquivos Xano versionados contêm GET `/consultas`, GET `/disponibilidades`, POST `/disponibilidades` e PATCH `/disponibilidades/{id}` no grupo `Sorriso Acesso`. As specs vigentes `agenda-consultas`, `gestao-disponibilidades` e `interface-agenda` já definem os requisitos comportamentais. A inspeção deste ambiente não encontrou `XANO_METADATA_TOKEN` nem `XANO_WORKSPACE_ID`; não foi feita chamada administrativa nem inferida a publicação a partir dos arquivos locais.

## Goals / Non-Goals

**Goals:** publicar as versões do repositório no workspace designado, validar as rotas no grupo oficial e documentar a evidência.

**Non-Goals:** alterar código de aplicação, schemas, regras de domínio ou contratos da interface; criar grupo Xano temporário; usar credenciais ou dados reais.

## Decisions

- Usar a Metadata API do Xano, com base `https://x8ki-letl-twmt.n7.xano.io/api:meta`, workspace configurado e credencial obtida do ambiente seguro.
- Comparar os endpoints existentes no workspace com as fontes versionadas antes de qualquer atualização. Publicar somente os quatro endpoints listados na proposta.
- Verificar contratos localmente sem chamadas de rede e executar integração real apenas no Xano publicado, opt-in e com dados fictícios, respeitando os limites de requisição.
- Não considerar uma alteração publicada até que a Metadata API confirme a operação e uma verificação do grupo principal confirme os contratos.

## Risks / Trade-offs

- Sem token administrativo e workspace, a publicação fica bloqueada; não se deve recorrer a uma API temporária, criar credenciais no repositório ou alegar publicação.
- Um endpoint publicado pode divergir do fonte local; comparar antes de atualizar e registrar a divergência sem sobrescrever comportamento fora deste escopo.
- Verificações com mutação exigem Conta de Acesso fictícia autorizada e plano de limpeza compatível com preservação histórica.
