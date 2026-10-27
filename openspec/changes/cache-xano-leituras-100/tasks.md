## 1. Especificação e contrato
- [ ] 1.1 Validar os artefatos com `openspec validate cache-xano-leituras-100 --strict` e disponibilizar o contrato ao responsável pelo cadastro de Paciente

## 2. Cache e sessão
- [ ] 2.1 Implementar helper session_state com hash de escopo, hit/miss/force, exceções e limpeza 401/403; verificar com testes unitários
- [ ] 2.2 Integrar invalidação integral no logout, expiração e troca de Conta de Acesso/perfil; verificar limpeza por testes

## 3. Integrações
- [ ] 3.1 Integrar todas as leituras GET de páginas fora do cadastro de Paciente, com namespace por parâmetros; verificar inventário de rotas
- [ ] 3.2 Adicionar força de leitura nos controles manuais e invalidadores de dependência após cada mutação bem-sucedida; verificar chamadas e dependências

## 4. Verificação
- [ ] 4.1 Testar contagem de GET em hit, navegação, force, mutações, identidades, logout, 401/403 e rede sem chamadas reais
- [ ] 4.2 Auditar buscas de GET no projeto e documentar páginas/rotas cobertas e restantes; executar testes relevantes e validação OpenSpec
