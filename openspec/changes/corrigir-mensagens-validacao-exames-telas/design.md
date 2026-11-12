## Context

O Xano já valida autorização, vínculos entre Paciente e Consulta, datas e transições de Exames. O cliente REST também possui validações cadastrais específicas, mas a interface de Exames e a edição de Paciente substituem parte desses erros por textos genéricos. A autorização continuará no backend; a validação local serve apenas para orientar a correção antes da requisição.

## Goals / Non-Goals

**Goals:**

- Dar feedback específico para campos obrigatórios, formato de data e observações do Exame.
- Mapear status HTTP do fluxo de Exames para mensagens seguras e acionáveis.
- Reaproveitar mensagens de validação já produzidas pelo cliente de Pacientes.
- Cobrir os caminhos de sucesso e erro com testes sem chamadas reais à rede.

**Non-Goals:**

- Alterar regras de autorização ou o modelo de dados do Xano.
- Criar envio de Exame para laboratório, profissional externo ou notificação.
- Refatorar todas as mensagens de leitura do aplicativo que já são adequadamente genéricas para falhas de carregamento.

## Decisions

1. **Validar no cliente REST e manter a validação no Xano.**
   `ClienteExames.solicitar` rejeitará identificadores ausentes, tipo vazio, data inválida/futura e observações acima do limite antes do POST. O backend continuará sendo a fonte de segurança e poderá rejeitar novamente valores adulterados.

2. **A tela exibirá a mensagem do erro somente quando ela for segura.**
   Para 400, a interface exibirá a mensagem sanitizada produzida pelo cliente; para 401, 403, 404, 409 e 429 usará textos de orientação por contexto. Falhas inesperadas continuarão com mensagem genérica, sem expor detalhes técnicos.

3. **O destino da solicitação permanece o domínio atual.**
   O Profissional solicita o Exame para o Paciente selecionado e vinculado à Consulta selecionada. A solicitação fica registrada no sistema como `Solicitado`; esta change não cria destinatário externo nem notificação.

4. **A edição cadastral preservará validações existentes.**
   A tela de Pacientes usará a mensagem segura já gerada por `validar_cadastro` quando o status for 400, em vez de descartá-la.

## Risks / Trade-offs

- [Mensagem retornada diretamente pelo backend pode ser ampla] → Exibir apenas mensagens já sanitizadas e sem dados clínicos; manter mapeamentos específicos para status de autorização e escopo.
- [Validação local pode divergir do Xano] → Não remover validações do backend e cobrir somente regras já previstas no contrato vigente.
- [Mudança de texto pode afetar testes de interface] → Atualizar testes para verificar o comportamento e as mensagens acionáveis.
