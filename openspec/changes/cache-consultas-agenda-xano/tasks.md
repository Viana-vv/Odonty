## 1. Cache da Agenda

- [x] 1.1 Reutilizar por vinte segundos as Consultas da mesma Conta de Acesso e data; verificar filtros sem uma segunda chamada em teste Streamlit.
- [x] 1.2 Invalidar o cache após alterações e logout; verificar expiração, troca de token e limpeza da sessão.
- [x] 1.3 Bloquear nova tentativa durante vinte segundos após falha sem transformar erro em lista vazia; verificar mensagem e número de chamadas.

## 2. Verificação

- [x] 2.1 Testar Consulta, filtros, estados vazios, atualização e formulários da Agenda com respostas fictícias e sem rede.
- [x] 2.2 Executar testes Python, JavaScript, OpenSpec estrito e integração real de leitura autorizada no Xano; registrar resultados no Pull Request.
