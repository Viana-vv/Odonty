## Context

O portal e seus testes locais já existem; a mudança é de verificação operacional dos contratos no grupo principal Xano. O repositório possui padrões de testes reais opt-in, mas esta suíte não deve usar Metadata API, criar grupos ou provisionar dados. Atualmente o ambiente de execução desta worktree contém `XANO_API_BASE_URL`, mas não oferece credenciais de Conta de Acesso de Paciente de teste.

## Goals / Non-Goals

**Goals:** verificar os contratos publicados sem mutações, usar apenas dados fictícios provisionados, manter segredo fora dos arquivos e diferenciar falha de teste de pré-requisito ausente.

**Non-Goals:** publicar ou editar APIs, criar identidade/dados no Xano, usar endpoints temporários, modificar o portal ou substituir testes unitários sem rede.

## Decisions

- Executar a verificação somente com opt-in explícito e variáveis de ambiente para URL, e-mail e senha da Conta de Acesso fictícia; nunca colocar os valores em argumentos de linha de comando ou logs.
- Usar apenas endpoints REST existentes do grupo principal: autenticação, identidade, Consultas, Registros Clínicos, Exames e logout.
- Fazer primeiro o login com identidade fictícia aprovada e verificar o perfil Paciente; enviar os GETs protegidos com a sessão retornada, sem identificador de Paciente fornecido pelo cliente.
- Usar fixtures somente para campos sintéticos efêmeros em memória; não comparar nem imprimir conteúdo clínico. Garantir logout em `finally` e descartar token local.
- Manter testes unitários e JavaScript sem rede; a integração publicada é uma suíte separada, opt-in.

## Risks / Trade-offs

- Uma Conta de Acesso válida e dados fictícios previsíveis precisam ser provisionados no Xano principal por responsável autorizado. Sem isso, a execução real fica bloqueada; não se deve criar ou presumir credenciais.
- A execução depende da disponibilidade do serviço publicado e pode confirmar somente o estado observado naquele momento.
- Mesmo sem mutações, uma conta de teste inadequada poderia revelar dados. Por isso a execução requer conta explicitamente fictícia e respostas não são gravadas nem exibidas em relatórios.

## Situação da verificação publicada

A suíte `tests/test_xano_autoatendimento_publicado.py` foi implementada com opt-in e sem mutações. A regressão local confirma que a suíte permanece ignorada sem habilitação. No ambiente desta worktree, `XANO_API_BASE_URL` está configurada, mas `XANO_AUTOATENDIMENTO_EMAIL` e `XANO_AUTOATENDIMENTO_SENHA` não estão disponíveis. A validação de login, isolamento e leituras no grupo publicado requer uma Conta de Acesso exclusivamente fictícia, provisionada e fornecida pelo responsável do Xano por canal seguro; nenhum segredo será inventado ou persistido.
