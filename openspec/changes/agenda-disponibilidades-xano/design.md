## Context

Os arquivos Xano versionados contêm GET `/consultas`, GET `/disponibilidades`, POST `/disponibilidades` e PATCH `/disponibilidades/{id}` no grupo `Sorriso Acesso`. As specs vigentes `agenda-consultas`, `gestao-disponibilidades` e `interface-agenda` já definem os requisitos comportamentais. A inspeção deste ambiente não encontrou `XANO_METADATA_TOKEN` nem `XANO_WORKSPACE_ID`; não foi feita chamada administrativa nem inferida a publicação a partir dos arquivos locais.

## Goals / Non-Goals

**Goals:** publicar as versões do repositório no workspace designado, validar as rotas no grupo oficial e documentar a evidência.

**Non-Goals:** alterar schemas, regras de domínio ou contratos REST; criar grupo Xano temporário; usar credenciais ou dados reais. A finalização autorizada em 29/10/2026 inclui somente os ajustes locais de data e cancelamento descritos abaixo.

## Decisions

- Usar a Metadata API do Xano, com base `https://x8ki-letl-twmt.n7.xano.io/api:meta`, workspace configurado e credencial obtida do ambiente seguro.
- Comparar os endpoints existentes no workspace com as fontes versionadas antes de qualquer atualização. Publicar somente os quatro endpoints listados na proposta.
- Verificar contratos localmente sem chamadas de rede e executar integração real apenas no Xano publicado, opt-in e com dados fictícios, respeitando os limites de requisição.
- Não considerar uma alteração publicada até que a Metadata API confirme a operação e uma verificação do grupo principal confirme os contratos.
- Inicializar a data da tela própria Nova Consulta pelo seletor diário da Agenda, com fallback para a data da clínica em `America/Sao_Paulo`. Alterações no formulário não devem modificar o filtro da Agenda.
- Após Cancelar, solicitar um rerun do Streamlit para que a navegação para Agenda seja renderizada imediatamente, sem enviar agendamento.
- Verificar os dois ajustes com AppTests sem rede, incluindo a reprodução da falha antes da correção.

## Risks / Trade-offs

- Sem token administrativo e workspace, a publicação fica bloqueada; não se deve recorrer a uma API temporária, criar credenciais no repositório ou alegar publicação.
- Um endpoint publicado pode divergir do fonte local; comparar antes de atualizar e registrar a divergência sem sobrescrever comportamento fora deste escopo.
- Verificações com mutação exigem Conta de Acesso fictícia autorizada e plano de limpeza compatível com preservação histórica.
