## 1. Backend e contrato

- [x] 1.1 Criar GET `/pacientes` autorizado no Xano e cliente Python; verificar dados mínimos, lista vazia, dados inválidos, sessão, permissões e falhas em testes unitários Python e JavaScript separados por rota e sem rede.

## 2. Interface

- [x] 2.1 Migrar a tela para o cache `pacientes` e testar busca, atualização, cadastro/edição e sessão; reproduzir Recepcionista abrindo Pacientes mesmo com opções da Agenda indisponíveis.

## 3. Integração e entrega

- [x] 3.1 Executar regressões e validação OpenSpec e atualizar a documentação com o contrato exclusivo.
- [x] 3.2 Publicar somente a nova rota Xano e verificar a listagem e a autorização sem alterar cadastros existentes.
- [ ] 3.3 Criar commit e Pull Request da Issue #146 com resultado dos testes e orientação de revisão.

## Verificação em 21/11/2026

- A rota exclusiva foi publicada por push limitado a `api/sorriso_acesso/pacientes_GET.xs`, após prévia sem alterações em tabelas ou registros.
- Verificação real: sem autenticação → 401; Recepcionista e Administrador → 200 com 15 Pacientes e somente `id`/`nome`; Profissional e Paciente → 403. Logout executado e as quatro Contas de Acesso fictícias criadas para verificação foram inativadas.
- Contratos JavaScript: 51 testes aprovados. Validação estrita OpenSpec e `git diff --check` sem erros.
- Regressão Python final: 347 testes aprovados, 7 subtestes aprovados e 1 caso preexistente excluído (`-k 'not falha_revalidacao'`), cobrindo contratos REST, listagem, roteamento, cache e cadastro de Paciente.
- A regressão ampliada encontrou `test_saida_limpa_dados[falha_revalidacao]` falhando também no código original de `HEAD`, comprovado por execução isolada antes de restaurar as alterações desta correção. Trata-se da limpeza do formulário após indisponibilidade da revalidação, fora do escopo da listagem. O teste permanece inalterado; a execução final das regressões exclui somente esse caso conhecido.
