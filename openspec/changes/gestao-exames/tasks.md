## 1. Contrato e cliente REST

- [x] 1.1 Definir modelos de entrada, saída e situações permitidas para Exame e verificar cobertura nos testes de contrato.
- [x] 1.2 Implementar cliente REST isolado para GET `/exames`, POST `/exames` e PATCH `/exames/{id}/situacao`, verificando autenticação, erros e ausência de dados de arquivo nos testes Python e JavaScript.

## 2. Backend Xano

- [x] 2.1 Criar a tabela e os endpoints de Exame com vínculo a Paciente, Consulta e Profissional, verificando o script/export em ambiente fictício.
- [x] 2.2 Aplicar autorização por perfil e vínculo clínico no Xano, verificando cenários de paciente próprio, profissional relacionado e acesso negado.
- [x] 2.3 Validar transições de situação, preservação de histórico e ausência de anexos, verificando respostas de sucesso e erro.

## 3. Tela Streamlit

- [x] 3.1 Implementar a tela de Exames com hierarquia, cores, espaçamento e estados visuais do kit Sorriso Mais, verificando renderização em estados carregando, vazio, sucesso e erro.
- [x] 3.2 Integrar formulário e listagem ao cliente REST sem expor resultado indevido, upload ou URL pública, verificando permissões e mensagens compreensíveis.

## 4. Verificação final

- [x] 4.1 Executar testes Python e JavaScript da change, lint/compilação e `openspec validate --strict`, corrigindo falhas antes do commit.
- [ ] 4.2 Executar cenários remotos somente em Xano temporário com dados fictícios e intervalo de rate limit, registrando o resultado real ou a limitação verificável.
- [x] 4.3 Revisar diff, confirmar que não há credenciais/dados reais e criar commit descritivo na branch da atividade.
