## 1. Diagnóstico e autenticação

- [x] 1.1 Reproduzir a submissão do formulário com AppTest cobrindo sucesso, credenciais rejeitadas, falha de identidade e indisponibilidade; confirmar limpeza da senha em todos os resultados.
- [x] 1.2 Comparar o contrato local e a rota publicada do Xano para `/auth/login` e `/auth/me`; corrigir somente a divergência comprovada e verificar autenticação de Conta de Acesso de Paciente ativa sem registrar credenciais ou dados pessoais.

## 2. Interface do Paciente

- [x] 2.1 Remover a frase sobre a equipe usar outro endereço e reorganizar o login do Paciente com identidade visual Sorriso Mais; verificar campos, rótulos e mensagem de erro com AppTest.
- [x] 2.2 Aplicar estilos próprios do portal, responsivos e acessíveis, e verificar visualmente em desktop e celular sem alterar o login da equipe.

## 3. Revisão

- [x] 3.1 Executar testes de sessão/login e contratos Python/JavaScript pertinentes, validar OpenSpec e revisar diff para garantir que não há credenciais nem mudanças de autorização fora do escopo.
