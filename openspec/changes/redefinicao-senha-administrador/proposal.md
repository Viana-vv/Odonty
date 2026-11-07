# Proposta — Redefinição de senha solicitada pelo Administrador

## Why

O Administrador precisa ajudar uma Conta de Acesso a recuperar o acesso sem conhecer ou escolher sua senha. Há autenticação e uma listagem de contas somente leitura; a inspeção remota também encontrou recuperação pública por OTP, ausente no repositório, que não atende à solicitação administrativa por link.

Esta change registra o plano dos três integrantes; a aprovação e os limites da primeira rodada estão abaixo. Aprovação das políticas não autoriza publicação. Nenhuma senha, conta, sessão ou configuração remota foi modificada durante a investigação.

**Registro de aprovação:** em07/11/2026 o usuário informou aprovação das políticas pelo grupo e autorizou a primeira parte local: contratos, estruturas e testes. Essa autorização não abrange telas, alterações/publicação no Xano ou envio de e-mails. O escopo efetivamente entregue está em `docs/redefinicao-senha-local.md` e na seção7 de `tasks.md`; as decisões abaixo registram as recomendações aprovadas, sem autorizar ativação automática.

## What Changes

- Disponibilizar a listagem existente de Contas de Acesso no menu autorizado, preservando consulta por Administrador/Recepcionista, e oferecer somente ao Administrador “Enviar link de redefinição de senha”. Não reconstruir o painel.
- Confirmar a solicitação com identificação da conta e e-mail mascarado; enviar exclusivamente ao e-mail da Conta de Acesso, sem destinatário ou URL de retorno fornecidos pelo cliente.
- Propor três contratos novos: POST de solicitação administrativa idempotente, GET exclusivo de consulta de resultado sem efeitos colaterais e POST de confirmação pública por token específico; validar sessão e autorização administrativa no Xano.
- Propor link válido por 15 minutos, uso único, armazenamento apenas de hash, consumo e mudança de senha atômicos, revogação de todas as sessões e invalidação de solicitações anteriores.
- Reutilizar a política encontrada de 12 a 128 caracteres e o campo protegido de senha do Xano; manter a senha anterior até a conclusão.
- Reutilizar funções de e-mail somente após verificar sua adequação, configuração e remetente; distinguir aceitação pelo provedor, falha e resultado incerto. Presença de função não comprova entrega.
- Acrescentar superfície Streamlit sem login, isolamento do token, auditoria mínima, limites de frequência, testes sem rede e mensagens seguras.
- Separar `estado_envio` de `estado_link`, com transições terminais e respostas tardias determinísticas; distinguir também resultado incerto da própria troca de senha, sem repetição automática.
- Usar flag pública de novos envios no Streamlit, seguindo a configuração por ambiente existente, e flag independente no Xano como controle definitivo. A consulta da Recepcionista permanece disponível; desligar novos envios não invalida links já emitidos.
- Condicionar a ativação à reconciliação do OTP remoto e à coordenação mínima de login/trocas de senha: impedir reutilização cruzada de solicitações e sessões de senha anterior sem substituir silenciosamente o contrato público existente.

### Decisões propostas para aprovação

1. Exceção restrita à regra atual de tokens em URLs: permitir somente o token temporário e de uso único de redefinição no link. Tokens de sessão e credenciais administrativas continuam proibidos em URLs. Sem aprovação e proteção de logs na implantação, o envio permanece desabilitado; alternativa: link sem segredo e código separado digitado pelo destinatário, a revisar antes de implementar.
2. Contas destinatárias precisam estar ativas; bloquear contas inexistentes, inativas e bloqueadas sem alterar sua situação. Permitir solicitação para a própria conta ativa do Administrador, com a mesma confirmação e limites.
3. Limites iniciais propostos: 10 solicitações por hora por Administrador, 3 por hora por destinatário e intervalo mínimo de 60 segundos por destinatário; reenvio explícito invalida links anteriores mesmo se o novo envio falhar.
4. Manter a divergência de duração normal de sessão fora desta change: a spec vigente diz uma hora; export e delta arquivado dizem até oito. A revogação após redefinição independe desse prazo. O grupo deve reconciliar essa política separadamente, sem sincronização automática neste trabalho.
5. Aprovar a integração de segurança com o OTP remoto existente antes de ativar o link: preservar entradas/saídas conhecidas do OTP, coordenar consumo/troca e invalidar solicitações cruzadas. Se o grupo não aprovar esse trabalho compartilhado, o recurso por link não será ativado; não há promessa de isolamento seguro sem essa coordenação.
6. Recomenda-se janela de idempotência/consulta de 30 dias desde a reserva no servidor, com retenção mínima correspondente e UUIDv7 de primeira criação recente. Após remoção, o timestamp imutável do mesmo identificador impede recriá-lo; não se promete replay indefinido. É proporcional ao projeto e evita um registro permanente só para deduplicação.
7. Recomenda-se desligamento normal apenas de novos envios, preservando consulta autenticada e confirmação de links vigentes. Revogação emergencial/rollback invalida explicitamente os links, sem reviver sessões ou senhas anteriores. O prazo inicial de transporte recomendado é 20 segundos, aplicado como limite total real e registrado por operação, não uma suposição de entrega.

## Capabilities

### New Capabilities

- `redefinicao-senha`: solicitação administrativa, envio, confirmação pública e ciclo de vida seguro da redefinição de uma Conta de Acesso.

### Modified Capabilities

- `consulta-contas-acesso`: tornar a tela existente alcançável e permitir a ação restrita, mantendo consulta e demais limites atuais.
- `acesso-autenticado`: propor a exceção delimitada de transporte do token de redefinição e distinguir logout individual de revogação global após troca de senha.

## Impact

- Pontos existentes reutilizáveis: `sorrisomais/pagina_contas_acesso_xano.py`, `api_contas_acesso.py`, `navegacao.py`, `paginas_equipe.py`, `app.py`, `sessao.py`, transporte REST e exports em `backend/xano/`.
- Novos recursos propostos: registros de operação/token, coordenação por conta e limites/auditoria, função de envio adaptadora, duas rotas POST e uma GET. Não são endpoints publicados.
- Dependências: serviço de e-mail realmente configurado, remetente autorizado, URL HTTPS pública fixa e proteções de logs/headers no host; evidências e limitações ficam em `design.md`.
- Recursos remotos confirmados: funções `sendgrid_basic_send` e `sendgrid_dynamic_send`, além de `POST auth/recuperacao-senha`, `auth/recuperacao-senha/validar` e `auth/recuperacao-senha/trocar` no grupo Sorriso Acesso. Não são contratos locais versionados nem prova de entrega. O helper básico mantém histórico; não pode receber o link sensível sem proteção da cadeia de logs.
- Coordenação: a change `contas-acesso-65` excluiu integração no menu; a integração arquivada de telas órfãs não incluiu Contas. Confirmar com os colegas trabalho recente não presente nas referências locais antes de editar esses pontos.
- Fora do escopo: MFA, cadastro público, reativação/desbloqueio, edição de perfis/e-mail, redefinição pelo próprio Administrador em nome do titular, novo painel, prazo normal da sessão, mudanças clínicas, publicação e envio de e-mails nesta etapa.
- Estado inicial preservado: branch `config/129-inicializacao-local-windows`, commit `6683a443`, arquivo não rastreado `docs/retomada.md`. Sem Issue/branch nova, commit ou push nesta etapa por instrução expressa do usuário; seguir o fluxo Git do grupo somente após aprovação.
