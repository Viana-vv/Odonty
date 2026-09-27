## 1. Preparação

- [x] 1.1 Revisar proposta, specs e design, confirmando campos, perfis autorizados e criação sem login; registrar revisão antes de implementar.
- [ ] 1.2 Criar Issue e branch vinculada, preservando alterações existentes; verificar vínculo e ausência de commits diretos na main.
- [x] 1.3 Preparar ambiente Python isolado e dependências do projeto; executar a suíte local existente e registrar a linha de base atual.
- [x] 1.4 Inspecionar metadados de Paciente, Prontuário e APIs legadas no Xano; registrar mapeamento físico no design e verificar compatibilidade sem modificar dados existentes.

## 2. Persistência e API Xano

- [x] 2.1 Preparar estruturas de Paciente, Prontuário e operação idempotente com índices; verificar CPF obrigatório e único, vínculo único do prontuário e unicidade composta da operação em dados fictícios.
- [x] 2.2 Implementar POST /pacientes e validação de campos no backend; criar testes reais opt-in de sucesso, limites, CPF inválido, datas, contatos, campos obrigatórios vazios e campos extras, verificando ausência de gravação nas rejeições.
- [x] 2.3 Aplicar autenticação e autorização atual de Administrador/Recepcionista; testar chamadas diretas sem sessão, com sessão expirada/revogada, conta bloqueada/inativa, perda de perfil, Profissional e Paciente.
- [x] 2.4 Implementar transação e comprovante de operação com hash do payload normalizado, conforme decisão acadêmica registrada no design; testar replay, payload divergente, concorrência da mesma chave e concorrência de CPF em chaves diferentes, sem dados parciais.
- [x] 2.5 Verificar rollback por falha induzida em ambiente de teste isolado e retorno seguro de erro; comprovar ausência de Paciente, Prontuário ou comprovante parcial e remover somente infraestrutura temporária de teste.
- [x] 2.6 Desativar histórico sensível e configurar no-store; testar respostas mínimas e ausência de dados pessoais/segredos em erros e histórico.
- [x] 2.7 Documentar contrato, estratégia de idempotência e execução/limpeza dos testes reais no README; verificar instruções sem expor valores secretos e preservar registros fictícios conforme o domínio.

## 3. Cliente REST e interface

- [x] 3.1 Implementar normalização e validações de paciente em módulo próprio; testar limites, máscara/CPF, nascimento, contatos compartilhados e campos obrigatórios, sem reutilizar regras de CRO.
- [x] 3.2 Integrar POST /pacientes ao cliente REST, validar resposta e mapear códigos permitidos; testar 201, 400, 401, 403, ambos os 409, 429, timeout e resposta incompatível sem repetição automática.
- [x] 3.3 Adicionar navegação de paciente para Administrador e Recepcionista; testar múltiplos perfis, navegação adulterada, perda de perfil e preservação do cadastro de Profissional exclusivo de Administrador.
- [x] 3.4 Implementar formulário e ciclo da chave idempotente; testar sucesso, erros corrigíveis, duplo envio, payload preservado em resultado incerto e tentativa manual usando a mesma operação.
- [x] 3.5 Ampliar limpeza de estado para paciente em Voltar, logout, expiração e falha de revalidação; testar ausência dos campos após saída e preservação da identidade da equipe após sucesso.
- [x] 3.6 Atualizar README com campos, perfis e limites do fluxo; verificar correspondência com os rótulos reais e explicar que o cadastro não cria login do paciente.

## 4. Integração e entrega

- [x] 4.1 Executar regressão local e integração Xano com dados fictícios; registrar separadamente resultados atuais e pendências, inclusive preservação de autenticação e cadastro de Profissional.
- [x] 4.2 Verificar o fluxo completo pelo navegador como Administrador e Recepcionista em computador, tablet, celular e teclado; registrar evidências sem dados pessoais ou credenciais.
- [x] 4.3 Executar openspec validate cadastro-paciente-equipe --strict e revisar o diff; verificar aprovação da change, ausência de segredos e registrar separadamente o TBD preexistente da spec principal.
- [ ] 4.4 Publicar PR ligado à Issue com evidências e solicitar revisão do grupo; verificar que o escopo contém somente cadastro de Paciente e dependências necessárias.
- [ ] 4.5 Após conclusão verificada, conciliar e sincronizar primeiro a dependência cadastro-profissional-admin e arquivar esta change pela CLI; verificar que ambos os cadastros e suas permissões permanecem nas specs principais, sem edição manual.

## Retomada — 27/09/2026

Implementação autorizada pelo usuário nesta sessão. Revisados proposta, design e ambas as specs: nome e nascimento obrigatórios; regra inicial de CPF, e-mail e celular opcionais substituída em 27/09/2026 por decisão do usuário de tornar os seis campos obrigatórios. Cadastro exige login da equipe e perfil Administrador ou Recepcionista; não cria login do Paciente. Branch local: feat/cadastro-paciente-equipe. Issue e inspeção remota pendentes de acesso. Nenhuma credencial Xano está configurada nesta máquina.


### Evidências locais e pendências

- Ambiente Python 3.12 isolado preparado em `.venv`; linha de base: 110 testes existentes passaram.
- Regressão integrada: 188 testes passaram (110 existentes e 78 novos). Após acrescentar dois casos de resposta inválida, a suíte de pacientes passou com 80 testes.
- Interface, normalização, contrato REST, rejeição de token vazio, navegação por perfis, resultado incerto, reenvio manual, preservação e limpeza de dados cobertos com API simulada. Essas evidências não comprovam autorização, unicidade ou transações no Xano.
- Interface desabilitada por padrão; `XANO_CADASTRO_PACIENTE_HABILITADO=1` somente após publicação e validação remota. A flag não é controle de segurança do backend.
- `openspec.cmd validate cadastro-paciente-equipe --strict` passou. Revisão do diff não encontrou credenciais nos arquivos adicionados. `git diff --check` nos arquivos alterados nesta implementação passou; o `.gitignore` já estava alterado e contém aviso preexistente de linha em branco ao final. Sua alteração foi preservada.
- O `TBD` preexistente continua em `openspec/specs/acesso-autenticado/spec.md:4`, sem edição manual.
- Metadados, backend, integração real, navegador em dispositivos, Issue, PR e arquivo permanecem pendentes. Não há XANO_API_BASE_URL, XANO_WORKSPACE_ID ou XANO_METADATA_TOKEN no processo nem nas variáveis persistentes User/Machine. A busca por integração Xano disponível também não encontrou plugin.
- Nenhuma tabela ou API remota foi criada/modificada. Não foi presumido mapeamento de Paciente/Prontuário sem a inspeção exigida no design.

### Inspeção e adaptação do Prontuário — 27/09/2026

- Autenticação da Metadata API confirmada com HTTP 200 usando o token atualizado persistido no ambiente do usuário. O processo anterior ainda herdava o token antigo; a indisponibilidade descrita na retomada anterior foi superada.
- Inspecionados schemas de paciente (883766) e prontuario (883771) e operações do grupo Sorriso Acesso (434156). Não foram consultados registros clínicos.
- Usuário aprovou preservar a tabela legada prontuario e criar uma estrutura separada para o Prontuário único. Publicada prontuario_paciente (899868), com paciente_id obrigatório, aberto_em, situacao e índice único por paciente_id. Schema e índice confirmados por nova leitura da Metadata API; schema legado preservado. Fonte em backend/xano/table/prontuario_paciente.xs.
- A tabela paciente (883766) exige telefone; usuário confirmou telefone obrigatório e, depois, aprovou que todos os seis campos cadastrais sejam obrigatórios.
- Regressão local: 196 testes passaram em tests/test_acesso.py, tests/test_interface.py, tests/test_profissionais.py e tests/test_pacientes.py. OpenSpec validado com --strict. Esses testes não comprovam a integração real do novo cadastro.
- Restaurada a origem da API de aplicação no teste real de expiração; chamadas de metadados continuam usando exclusivamente XANO_METADATA_BASE_URL.
- Tarefa 2.1 continua pendente: a criação da tabela de Prontuário é parcial; faltam os ajustes de Paciente, operação idempotente e verificações reais com dados fictícios. Nenhum endpoint de Paciente foi publicado e a interface continua desabilitada por padrão. Progresso permanece 9/22 tarefas completas.

### Decisão: telefone obrigatório

- Usuário determinou manter telefone obrigatório no cadastro de Paciente. Celular é obrigatório e separado do telefone. A decisão substitui a proposta de tornar telefone opcional e resolve a pendência anterior.
- Proposta, design e spec atualizados: cadastro mínimo com nome, nascimento e telefone; rejeitar telefone ausente, nulo, vazio, de tipo incorreto ou inválido; normalizar 10 ou 11 dígitos e permitir contato compartilhado.
- Incluir telefone entre os seis campos normalizados da impressão de idempotência. Validador, cliente REST, formulário, preservação dos seis campos e documentação local foram ajustados. Suíte local posterior: 196 testes aprovados. Schema do Prontuário separado criado. A integração real de criação no Xano e a coluna celular são parciais; validação/autorização real do endpoint continuam pendentes.


### Decisão: todos os campos obrigatórios — 27/09/2026

- Usuário confirmou que telefone permanece obrigatório e esclareceu que todos os seis campos do formulário devem ser preenchidos: nome, nascimento, telefone, CPF, e-mail e celular.
- Validação local, normalização, formulário, cliente REST, preservação do conteúdo da operação e README atualizados. CPF, telefone, e-mail e celular são validados; contatos podem ser compartilhados.
- Verificação: 196 testes passaram e `openspec validate cadastro-paciente-equipe --strict` passou. Os testes locais não cobrem o POST real de Paciente; as tarefas 2.x e integração Xano permanecem pendentes.

- Campo `celular` adicionado à tabela `paciente` pela Metadata API; campo não obrigatório para registros legados, mas exigido pelo novo contrato. A tarefa 2.1 permanece parcial até os índices, comprovante e idempotência.

### Correções autorizadas e verificadas — 27/09/2026

- Usuário autorizou corrigir as divergências identificadas entre o rascunho do backend e a especificação.
- Corrigidos no endpoint versionado: formato e dois dígitos verificadores do CPF; nascimento com calendário gregoriano (incluindo bissextos), ano mínimo 0001 e limite de hoje em America/Sao_Paulo; gravação explícita da situação ativa e das datas de criação/atualização.
- Auditoria autenticada no Xano retornou somente contagens: 0 Pacientes, 0 CPFs duplicados, 0 fora da normalização e 0 ausentes. Criado e confirmado índice único de CPF (5b24926c), adicionados situacao e atualizado_em e exportado schema para backend/xano/table/paciente.xs. Nenhum dado preexistente alterado.
- Testes reais: 26 passaram em tests/test_xano_pacientes_real.py. Compilaram o trecho de validação do endpoint e verificaram CPFs inválidos, máscara, dígitos Unicode, datas impossíveis/futuras, anos bissextos e limites, além do schema remoto. Grupo temporário removido e Conta de Acesso fictícia inativada. Nenhum Paciente/Prontuário criado.
- Regressão local: 196 passaram; os 26 testes reais foram ignorados corretamente sem a flag opt-in.
- As tarefas 2.1 e 2.2 continuam parciais: o teste isolado não comprova persistência, concorrência, transação, idempotência ou a matriz completa de autorização. O POST completo não foi publicado e a interface continua desabilitada por padrão. No rascunho, ainda é necessário concluir consulta composta da operação, tratamento de concorrência/reconsulta após rollback e configuração segura da chave HMAC antes da publicação.
- Progresso mantido em 9/22, sem marcar tarefas amplas como concluídas apenas com estas correções.

### Retomada sem chave — 27/09/2026

- Compilação Xano confirmada para POST completo e auxiliares temporários autenticados.
- 7 testes reais passaram (falha segura sem chave, três formatos JSON rejeitados sem gravação, schema e unicidade composta do comprovante, UUID malformado e histórico desativado). Nenhum Paciente/Prontuário foi criado nesta bateria.
- 196 testes locais passaram na bateria anterior. `openspec validate cadastro-paciente-equipe --strict` passou.
- Tabelas confirmadas: Paciente com índice único de CPF e campos situacao/atualizado_em; Prontuário paciente único; comprovante com Conta de Acesso, UUID, HMAC e Paciente obrigatórios, índice composto único.
- Progresso segue 10/22 tarefas completas. Tarefas amplas 2.1–2.6 e 4.1–4.4 permanecem abertas até os testes reais completos, navegador e entrega. Em 27/09/2026, o usuário autorizou remover a dependência HMAC e usar SHA-256 no Xano, exclusivamente com dados fictícios.


### Integração Xano sem chave — 27/09/2026

- Usuário autorizou remover CADASTRO_PACIENTE_HMAC_SECRET por se tratar de projeto acadêmico e a Metadata API não permitir essa configuração no plano gratuito. O endpoint calcula SHA-256 do payload normalizado. A coluna física vazia `impressao_hmac` foi mantida por compatibilidade. O uso é restrito a dados fictícios.
- Integração real: 62 testes passaram, cobrindo criação, replay idêntico, divergência, normalização, duplicidade inclusive Paciente inativo, contatos compartilhados, campos inválidos/ausentes, autorização por perfil e situação, sessão ausente/revogada/expirada, rollback, concorrência, schema, no-store e histórico desativado. Contas e Pacientes de teste foram inativados; grupo temporário removido; Prontuários e comprovantes preservados.
- Regressão local: 196 testes passaram. `openspec.cmd validate cadastro-paciente-equipe --strict` passou. Progresso: 19/22 tarefas; Issue/PR e sincronização/arquivo continuam pendentes.

- Endpoint POST /pacientes publicado no grupo principal do Xano (ID 4072582); smoke test real de criação e replay passou. Paciente e Conta de Acesso fictícios inativados; histórico de Prontuário/comprovante preservado. Flag local XANO_CADASTRO_PACIENTE_HABILITADO=1 persistida para a próxima inicialização do Streamlit.

- Navegador: 1 teste Playwright passou para Administrador e Recepcionista em Chrome, nas larguras 1440, 768 e 390 px; campos, foco pelo teclado e ausência de rolagem horizontal confirmados. Seis capturas fictícias salvas em `test-results/cadastro-paciente/`; duas contas de teste inativadas; nenhum Paciente criado.
