## 1. Especificação e navegação
- [x] 1.1 Implementar visão do Profissional na página inicial usando apenas Consultas do Xano e conferir com o teste de interface.
- [x] 1.2 Ligar atalhos existentes para Agenda e Prontuário e conferir seus controles no teste Streamlit.
- [x] 1.3 Tratar estados vazio, sessão inválida, permissão e falha de API; revisar caminhos de erro e estado vazio nos testes.

## 2. Verificação
- [x] 2.1 Reutilizar os testes Python e JavaScript existentes, separados por rota, para GET /consultas e confirmar que não fazem rede real.
- [x] 2.2 Executar testes pertinentes e revisar diff, privacidade e estado Git; os testes focados passaram e o diff não contém segredos nem conteúdo clínico.
- [x] 2.3 Verificar configuração de smoke; não executar porque não existe `.env` nem credencial de teste configurada, apesar de haver URL de API no ambiente.
