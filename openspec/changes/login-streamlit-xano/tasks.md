## 1. Resolver pré-requisitos e revisar

Checklist preliminar: as etapas posteriores dependem da aprovação dos contratos e permissões.

- [x] 1.1 Aprovar método de login e campos; e-mail e senha aprovados pelo usuário e registrados no design.
- [x] 1.2 Revisar e aprovar o contrato proposto POST /auth/login, GET /auth/me e POST /auth/logout no design; verificar rotas, métodos, payloads, respostas e erros documentados sem segredos.
- [x] 1.3 Aprovar a matriz proposta de identificação própria para os três perfis e página comum para múltiplos perfis; verificar tabela explícita sem permissões presumidas.
- [x] 1.4 Aprovar a política proposta de uma hora, sem renovação, nova entrada após perda de estado e revogação da sessão atual no logout; verificar regras documentadas e suporte previsto no Xano.
- [x] 1.5 Criar Issue, vincular branch e revisar os quatro artefatos; verificar referências e aprovação registradas antes do Apply.

## 2. Preparar Xano

- [ ] 2.1 Inspecionar conexão, estruturas e configuração de logs e configurar o contrato aprovado com Conta de Acesso e Sessão de Acesso; verificar respostas reais compatíveis e ausência de mudanças fora do escopo.
- [ ] 2.2 Configurar autorização e contas fictícias; verificar diretamente na API rejeição de conta bloqueada/inativa, ausência de autenticação e falta de permissão.

## 3. Implementar interface e integração

- [ ] 3.1 Preparar Python/Streamlit separando interface, API, configuração e sessão; verificar execução conforme comandos documentados.
- [ ] 3.2 Preparar mascote sem placeholders e formulário verde Sorriso+; verificar computador, tablet, celular e teclado.
- [ ] 3.3 Integrar autenticação e identidade; verificar com simulação campos inválidos, sucesso, credenciais incorretas, respostas vazias/malformadas, timeout e erros sem segredos.
- [ ] 3.4 Implementar sessão, expiração, acesso inicial e logout; verificar isolamento de sessões e retorno após saída conforme contrato.
- [ ] 3.5 Tratar processamento e submissões duplicadas; verificar comportamento após sucesso e erro.

## 4. Verificar e documentar

- [ ] 4.1 Executar no Xano real login válido/inválido, identidade, conta bloqueada/inativa, expiração, logout, replay após revogação, logout repetido e após perda de permissão, segunda sessão preservada e autorização dos perfis; registrar evidências fictícias separadas dos testes simulados.
- [ ] 4.2 Verificar rede, campos, acesso direto sem autenticação/permissão e tentativa de adulterar perfil; registrar resultado esperado e obtido sem segredos.
- [ ] 4.3 Documentar dependências, execução, variáveis, contratos e limitações; verificar reprodução pelo README.
- [ ] 4.4 Revisar diff e critérios da spec; verificar ausência de dados reais, credenciais e alterações fora do escopo.

## 5. Revisão e arquivo

- [ ] 5.1 Abrir PR ligado à Issue com instruções e resultados de testes e solicitar revisão de integrante; verificar referências.
- [ ] 5.2 Após conclusão e integração real validada, arquivar pelo OpenSpec; verificar tarefas concluídas e sincronização pela ferramenta, sem editar manualmente openspec/specs.



