## 1. Contratos Xano

- [x] 1.1 Implementar GET administrativo com sessão válida, campos permitidos e perfis autorizados; verificar export com teste Python e JavaScript.
- [x] 1.2 Implementar PATCH de situação exclusiva do Administrador com validação estrita e sem remoção de históricos; verificar export com teste Python e JavaScript.
- [x] 1.3 Verificar que Profissional inativo não pode receber novas Consultas e que as existentes permanecem intactas por inspeção/teste dos contratos existentes.

## 2. Cliente e interface

- [x] 2.1 Implementar métodos REST e validação de dados de resposta; verificar cenários de sucesso, sessão/erro e ausência de campos com testes Python sem rede.
- [x] 2.2 Atualizar cartões com CRO, especialidade, e-mail, telefone e situação, tratando valores nulos; verificar campos apresentados e grade responsiva em testes de interface.
- [x] 2.3 Exibir ação de situação apenas para Administrador, pedir confirmação e recarregar após sucesso; verificar sucesso e erro com testes de interface sem rede.
- [x] 2.4 Confirmar que Recepcionista consulta sem controles e perfis não autorizados não fazem chamadas; verificar com testes de interface.

## 3. Revisão

- [x] 3.1 Executar testes Python e JavaScript relacionados e validar OpenSpec; registrar os comandos e resultados.
- [x] 3.2 Revisar diff e verificar ausência de segredos e alterações fora do escopo com `git diff --check` e `git status`.
- [x] 3.3 Confirmar no relatório a pendência de aplicar os exports na instância Xano, caso as credenciais permaneçam indisponíveis.
