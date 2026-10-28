## 1. Diagnóstico e contrato

- [ ] 1.1 Reproduzir e documentar as regressões em `tests/test_profissionais.py` com execução isolada e resultado registrado
- [ ] 1.2 Definir cenários de preservação de formulário, cache, códigos HTTP e logout e validar a change com OpenSpec

## 2. Correção

- [ ] 2.1 Corrigir a navegação/estado do cadastro e verificar que editar campos mantém a tela e reutiliza Especialidades
- [ ] 2.2 Alinhar mensagem de logout ao prazo de uma hora e verificar teste unitário de sessão
- [ ] 2.3 Executar testes de cadastro, cache, erros 400/401/403/409/429/503, logout, campos e autorização sem rede real

## 3. Revisão

- [ ] 3.1 Remover artefatos de cache e verificar `git status` para confirmar que o diff contém somente arquivos da change
