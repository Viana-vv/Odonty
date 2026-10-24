## 1. Xano e edição do Paciente

- [x] 1.1 Corrigir a resposta da rota GET para dados opcionais e cobrir a regressão no teste de contrato JavaScript.
- [x] 1.2 Compilar os fontes GET/PATCH em ambiente Xano temporário e publicar as duas rotas no grupo `Sorriso Acesso`.
- [x] 1.3 Testar leitura e atualização real como Recepcionista usando apenas Conta de Acesso e Paciente fictícios; inativar os registros de teste e confirmar o resultado.

## 2. Navegação da equipe

- [x] 2.1 Fixar o menu em telas largas e manter o fluxo atual em viewport estreita.
- [x] 2.2 Validar rolagem de tela longa em desktop e navegação em celular sem sobreposição ou rolagem horizontal.

## 3. Verificação

- [x] 3.1 Executar testes Python e JavaScript pertinentes, validar OpenSpec em modo estrito e revisar o diff.

## 4. Correção das regressões identificadas no uso

- [x] 4.1 Reproduzir a falha com campos cadastrais vazios e permitir carregar esses valores, mantendo a validação obrigatória ao salvar.
- [x] 4.2 Reproduzir a rolagem em `stMain`, fixar a coluna correta e confirmar que o conteúdo rola sem deslocar o menu.
- [x] 4.3 Exercitar no navegador, com HTTP fictício e cliente REST real, abertura, preenchimento, salvamento, fechamento e reabertura do cadastro antigo como Recepcionista.
- [x] 4.4 Repetir o fluxo completo no navegador contra o Xano real, com dados fictícios e intervalo entre requisições; inativar os registros criados.
- [x] 4.5 Executar os testes pertinentes, validar OpenSpec e revisar o diff da nova branch.

### Evidências da revalidação

- Antes da correção, a rolagem de 600 px em `stMain` deslocava o menu de 0 para -600 px; o GET com campos vazios também falhava no teste unitário.
- Testes Python de listagem, edição, GET/PATCH e validação cadastral: 138 passaram.
- Contratos JavaScript GET/PATCH: 2 passaram.
- `tests/visual/conferir_agenda_ficticia.py`: passou com rolagem real, viewport móvel e abertura/salvamento/reabertura de cadastro incompleto via cliente REST real e HTTP fictício.
- `tests/test_xano_paciente_navegador.py::test_recepcionista_completa_cadastro_antigo_no_xano_real`: passou em 62,49 s; intervalo mínimo de 3,1 s nas chamadas do app e limpeza por inativação confirmada para os dois registros fictícios.
- OpenSpec em modo estrito e `git diff --check`: passaram.
