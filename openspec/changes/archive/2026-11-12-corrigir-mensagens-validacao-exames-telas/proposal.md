## Why

Algumas telas transformam erros corrigíveis da API em mensagens genéricas, impedindo que a pessoa saiba qual campo ou vínculo precisa ser corrigido. O caso mais visível ocorre ao solicitar Exame como Profissional, quando campos ausentes ou dados inválidos acabam apresentados apenas como “Confira os dados e tente novamente”.

## What Changes

- Validar no cliente REST os campos obrigatórios e a data da solicitação de Exame antes do envio.
- Exibir no formulário de Exames mensagens específicas para validação, sessão expirada, permissão, recurso fora do escopo, conflito e indisponibilidade.
- Preservar mensagens seguras e acionáveis também ao atualizar a situação de um Exame.
- Corrigir a tela de edição de Paciente para não esconder as mensagens específicas de validação cadastral.
- Manter mensagens sem dados clínicos, credenciais, stack trace ou detalhes internos.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `exames`: mensagens compreensíveis para falhas corrigíveis e confirmação do escopo da solicitação.
- `edicao-paciente`: preservação de mensagens de validação cadastral na interface.

## Impact

- Frontend Streamlit: `sorrisomais/pagina_exames_xano.py` e `sorrisomais/pagina_pacientes_xano.py`.
- Cliente REST: `sorrisomais/exames_api.py` e mapeamento seguro de erros em `sorrisomais/api.py`.
- Testes unitários Python e contratos existentes das rotas de Exames.
- Nenhuma alteração de banco, tecnologia, autorização ou contrato de persistência do Xano.
