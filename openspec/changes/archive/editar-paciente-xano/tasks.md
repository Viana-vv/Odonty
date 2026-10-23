## 1. API Xano

- [x] 1.1 Criar `GET /pacientes/{paciente_id}` com validação de sessão, perfil administrativo e resposta cadastral mínima; cobrir autorização, ausência, erro e sucesso em testes Python e JavaScript isolados por rota.
- [x] 1.2 Criar `PATCH /pacientes/{paciente_id}` com autorização, validação integral, CPF único e atualização somente dos campos permitidos; cobrir cenários de sucesso e rejeição em testes Python e JavaScript isolados por rota.

## 2. Cliente e interface

- [x] 2.1 Implementar métodos GET/PATCH no cliente REST, normalização e mensagens seguras; verificar payloads, validações locais e mapeamento de erros com testes unitários sem rede.
- [x] 2.2 Integrar formulário de edição à listagem Streamlit seguindo a referência sem campo clínico; verificar carregamento, salvar, cancelar, erros e atualização visual em testes de interface.

## 3. Verificação

- [x] 3.1 Executar testes Python e JavaScript das rotas e da interface, validar a change com `openspec validate editar-paciente-xano --strict` e revisar diff para confirmar ausência de alteração clínica, credenciais e dados reais.
- [x] 3.2 Smoke não executado: `XANO_TESTAR_PACIENTE` não está habilitada e não há configuração administrativa de teste; a URL Xano configurada não basta para autorizar chamadas remotas. Registrar esta limitação para revisão do grupo.
