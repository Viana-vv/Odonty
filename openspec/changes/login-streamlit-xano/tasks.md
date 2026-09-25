## 1. Resolver pré-requisitos e revisar

Checklist preliminar: as etapas posteriores dependem da aprovação dos contratos e permissões.

- [x] 1.1 Aprovar método de login e campos; e-mail e senha aprovados pelo usuário e registrados no design.
- [x] 1.2 Revisar e aprovar o contrato proposto POST /auth/login, GET /auth/me e POST /auth/logout no design; verificar rotas, métodos, payloads, respostas e erros documentados sem segredos.
- [x] 1.3 Aprovar a matriz proposta de identificação própria para os três perfis e página comum para múltiplos perfis; verificar tabela explícita sem permissões presumidas.
- [x] 1.4 Aprovar a política proposta de uma hora, sem renovação, nova entrada após perda de estado e revogação da sessão atual no logout; verificar regras documentadas e suporte previsto no Xano.
- [x] 1.5 Criar Issue, vincular branch e revisar os quatro artefatos; verificar referências e aprovação registradas antes do Apply.

## 2. Preparar Xano

- [x] 2.1 Inspecionar conexão, estruturas e configuração de logs e configurar o contrato aprovado com Conta de Acesso e Sessão de Acesso; verificar respostas reais compatíveis e ausência de mudanças fora do escopo.
- [x] 2.2 Configurar autorização e contas fictícias; verificar diretamente na API rejeição de conta bloqueada/inativa, ausência de autenticação e falta de permissão.

## 3. Implementar interface e integração

- [x] 3.1 Preparar Python/Streamlit separando interface, API, configuração e sessão; verificar execução conforme comandos documentados.
- [x] 3.2 Preparar mascote sem placeholders e formulário verde Sorriso+; verificar computador, tablet, celular e teclado.
- [x] 3.3 Integrar autenticação e identidade; verificar com simulação campos inválidos, sucesso, credenciais incorretas, respostas vazias/malformadas, timeout e erros sem segredos.
- [x] 3.4 Implementar sessão, expiração, acesso inicial e logout; verificar isolamento de sessões e retorno após saída conforme contrato.
- [x] 3.5 Tratar processamento e submissões duplicadas; verificar comportamento após sucesso e erro.

## 4. Verificar e documentar

- [x] 4.1 Executar no Xano real login válido/inválido, identidade, conta bloqueada/inativa, expiração, logout, replay após revogação, logout repetido e após perda de permissão, segunda sessão preservada e autorização dos perfis; registrar evidências fictícias separadas dos testes simulados.
- [x] 4.2 Verificar rede, campos, acesso direto sem autenticação/permissão e tentativa de adulterar perfil; registrar resultado esperado e obtido sem segredos.
- [x] 4.3 Documentar dependências, execução, variáveis, contratos e limitações; verificar reprodução pelo README.
- [x] 4.4 Revisar diff e critérios da spec; verificar ausência de dados reais, credenciais e alterações fora do escopo.

## 5. Revisão e arquivo

- [ ] 5.1 Abrir PR ligado à Issue com instruções e resultados de testes e solicitar revisão de integrante; verificar referências.
- [ ] 5.2 Após conclusão e integração real validada, arquivar pelo OpenSpec; verificar tarefas concluídas e sincronização pela ferramenta, sem editar manualmente openspec/specs.




## Evidências finais — 23/09/2026

- Python 3.10.10: 54 testes locais aprovados em `tests/test_acesso.py` e `tests/test_interface.py`.
- Xano, workspace 149129, grupo Sorriso Acesso: 25 testes reais aprovados em 312,60 segundos. Relatório local: `test-results/xano-real.xml`.
- Verificados: campos obrigatórios/inválidos, três perfis internos e múltiplos perfis, somente Paciente, contas bloqueadas/inativas, credenciais incorretas, ausência/token inválido, identidade própria, revogação, replay, logout repetido e após perda de acesso, segunda sessão preservada e expiração efetiva.
- O plano não permite branches. A expiração foi comprovada em grupo temporário contendo cópias dos três endpoints com validade de oito segundos; o grupo foi removido ao final. O grupo principal continuou emitindo uma hora.
- A primeira rodada atingiu HTTP 429; a suíte foi ajustada para espaçar chamadas. Contas fictícias da rodada anterior foram inativadas. A rodada final e sua limpeza passaram.
- Conta de Acesso usa campo password; a transformação da senha foi conferida. Histórico desativado nos endpoints e função; histórico do grupo permaneceu vazio após os testes.
- Playwright: computador 1440 px, tablet 768 px e celular 390 px, sem rolagem horizontal, foco visível, navegação E-mail → Senha e senha mascarada. Capturas em `test-results/login-*.png`.
- Duplo clique em servidor simulado: uma chamada ao cliente; botão e campos desabilitados durante envio; retorno ao formulário após saída.
- Navegador → Streamlit → Xano real: entrada da conta fictícia, nome e Dentista exibidos, saída e formulário reabilitado com senha vazia.
- `XANO_API_BASE_URL` configurada no ambiente do usuário Windows. Conta fictícia de demonstração com credencial protegida por DPAPI local, ignorada pelo Git.
- Correção publicada somente em auth/login após prévia sem erros: util.get_raw_input e sintaxe da validação do prazo. Tabelas e APIs legadas preservadas.
- `git diff --check` e validação estrita do OpenSpec passaram. Revisão do conteúdo limitada a esta change; credenciais, cópias remotas e evidências temporárias não entram no Git.
