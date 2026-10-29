## Why

O Xano versionado já possui criação, consulta e retificação de Registros Clínicos, mas não há validação confirmada no grupo publicado. Além disso, as retificações append-only não são retornadas no histórico, impedindo a auditoria do conteúdo anterior e da justificativa.

## What Changes

- Explicitar e testar autorização no Xano para Profissional, Paciente e Recepcionista nas operações clínicas.
- Expor retificações vinculadas no histórico sem substituir o Registro Clínico original.
- Preservar autor, data, justificativa e conteúdo anterior em cada retificação.
- Confirmar no grupo Xano publicado as permissões, vínculos, histórico e retificação usando apenas dados fictícios, quando houver credenciais de teste.
- Manter a apresentação do Prontuário alinhada ao kit Sorriso Mais e validar seus estados no AppTest.
- Finalizar os estados já previstos de Nova Evolução: conservar o Paciente selecionado, atualizar Consultas dependentes e descartar o rascunho ao cancelar, salvar ou encerrar a sessão.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `registro-clinico`: leitura do histórico deve expor retificações append-only e garantir autorização dos perfis clínicos e administrativos.
- `interface-prontuario`: apresentação do histórico deve preservar e exibir versões retificadas e seus metadados de auditoria.
- `registro-evolucao-clinica`: seleções dependentes e estados do formulário devem preservar o vínculo Paciente/Consulta e a privacidade do rascunho.

## Impact

Afeta exports Xano das rotas de Registro Clínico, cliente Python, tela Streamlit, testes Python/JavaScript por rota e testes AppTest. A publicação e validação real dependem de acesso autorizado para o grupo Xano publicado e contas fictícias dos perfis envolvidos. Na finalização local de 29/10/2026 há configuração administrativa da Metadata API, mas não há sessões clínicas fictícias autenticadas disponíveis para executar essa validação. Nenhuma publicação ou chamada real foi realizada nesta finalização.
