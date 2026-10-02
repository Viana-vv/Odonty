## Context

Consulte `proposal.md` e os requisitos existentes em `openspec/specs/cadastro-profissional/spec.md` e `openspec/specs/acesso-autenticado/spec.md`. O repositório já contém as telas Streamlit, o cliente REST, testes unitários em Python e JavaScript e os exports Xano versionados para `GET /especialidades` e `POST /profissionais`. A change anterior está arquivada e os arquivos locais mostram uma movimentação de artefatos arquivados ainda não conciliada; esta retomada não deve apagar nem reorganizar esses arquivos.

## Goals / Non-Goals

**Goals:** reunir evidências atuais para cada requisito e fechar apenas as tarefas cuja implementação e verificação estejam comprovadas; registrar limitações de acesso com clareza.

**Non-Goals:** alterar contratos ou regras aprovadas, publicar endpoints sem inspeção, cadastrar dados reais, ou modificar agenda, prontuário e cadastro de Paciente.

## Decisions

1. **Auditar antes de corrigir.** Comparar os requisitos com código, exports Xano versionados e testes existentes. Alterar código somente para corrigir uma divergência comprovada dentro do escopo aprovado; atualizar a tarefa correspondente após a verificação.

2. **Executar somente testes unitários.** Substituir o transporte HTTP por doubles e validar método, rota, payload, resposta e erros sem rede. Os testes JavaScript comparam método e rota com os exports Xano versionados.

3. **Não inferir estado remoto a partir de testes locais.** Os testes unitários não comprovam configuração, permissões, atomicidade, concorrência ou disponibilidade dos endpoints publicados no Xano. Registrar essa limitação sem iniciar testes de integração ou navegador.

4. **Preservar escopo sem rede.** Não solicitar nem ler credenciais do Xano e não executar comandos que enviem requisições ao workspace.

5. **Preservar o estado pré-existente do Git.** Os artefatos arquivados atualmente aparecem como movimentados no diretório de trabalho. Não restaurar, mover ou remover esses arquivos como parte da auditoria. A branch desta retomada deve manter tais alterações sem commit até que seu responsável confirme o destino.

## Risks / Trade-offs

- **Teste restrito a doubles locais** → resultados não comprovam o comportamento do backend publicado nem substituem a validação remota antes de uso integrado.
- **Artefatos arquivados em estado divergente** → preservar as alterações e separar sua reconciliação da validação funcional.

## Migration Plan

Não há migração prevista. Executar a auditoria local, os testes unitários sem rede, validar o OpenSpec e atualizar o README com resultados e limitações. Nenhum endpoint ou dado remoto será alterado.
