## Why

A Recepcionista ainda recebe uma mensagem genérica ao editar Pacientes: a rota `PATCH /pacientes/{id}` não está publicada e a rota `GET /pacientes/{id}` publicada responde erro de execução. Além disso, o menu da equipe rola junto com o conteúdo, dificultando a navegação em telas longas.

## What Changes

- Corrigir e publicar no Xano as rotas GET e PATCH existentes para editar somente dados cadastrais, mantendo a autorização de Administrador e Recepcionista no backend.
- Fixar o menu da equipe durante a rolagem em telas largas e preservar o fluxo responsivo em telas estreitas.
- Permitir abrir para edição cadastros antigos com CPF, celular ou e-mail vazios, exigindo os campos válidos ao salvar.
- Verificar a rolagem do contêiner interno do Streamlit e completar, salvar e reabrir um cadastro antigo no navegador.

## Capabilities

### New Capabilities
- `edicao-paciente`: edição cadastral de Paciente pela equipe autorizada usando a rota PATCH publicada.

### Modified Capabilities
- `interface-equipe`: menu de navegação fixo em telas largas e comportamento responsivo em dispositivos estreitos.

## Impact

- Frontend: `assets/estilos.css` e verificação visual de `layout-equipe`.
- Xano: corrigir/publicar os endpoints versionados `pacientes_id_GET.xs` e `pacientes_id_PATCH.xs` no grupo `Sorriso Acesso`.
- Testes: contratos da rota de edição e comportamento responsivo do menu.
