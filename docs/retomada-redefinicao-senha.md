# Retomada — Redefinição de senha — 07/11/2026

- Repositório: `Viana-vv/Odonty`.
- Branch de trabalho: `feat/131-contratos-redefinicao-senha` (não integrar à main nesta etapa).
- Issue: https://github.com/Viana-vv/Odonty/issues/131.
- Change: `openspec/changes/redefinicao-senha-administrador`.
- Políticas aprovadas pelo grupo; primeira parte local concluída e aguardando revisão. Progresso:7 tarefas locais concluídas,30 pendentes.

## O que está salvo

Planejamento, contratos OpenAPI, cliente Python dos três contratos, UUIDv7 sem dependência nova, schemas Xano locais aditivos, flag desligada por padrão e testes Python/JavaScript sem rede. Relatório detalhado e comandos: `docs/redefinicao-senha-local.md`.

Última verificação:391 testesPython e10JavaScript passaram; validação estrita OpenSpec passou. Isso não comprova atomicidade, timeout ou integração OTP no Xano.

## Limites que continuam valendo

Não implementar telas, publicar no Xano, enviar e-mails ou modificar contas/senhas sem autorização da próxima etapa. Nenhuma rota nova foi publicada. A referência Python do backend é exclusivamente offline, não um serviço de produção. Manter recurso desligado.

Antes de ativar, faltam handlers Xano, prova isolada de transação/CAS e timeout total, compatibilidade OTP/login, remetente/URL pública e proteção de logs. Consultar tasks sem marcar como concluído o que só foi simulado.

## Para continuar

1. Abrir esta pasta e conferir `git status` e branch; em outra máquina, buscar/trocar para a branch remota correspondente.
2. Ler `AGENTS.md`, contexto em docs, esta change e relatório local antes de editar.
3. Revisar esta primeira entrega. Próxima rodada possível: integrar menu/formulários com transporte simulado, ainda com envio real desligado; combinar autorização e escopo antes.
4. `.venv-win` usa Python3.12.10; `.venv` antigo aponta para Python ausente. UUIDv7 nativo não existe em3.12; o módulo usa stdlib compatível com3.10+.
5. Perfil CLI local Xano `odonty` está autenticado no workspace149129/v1. Credenciais ficam fora do repositório e não devem ser copiadas para docs, código, capturas ou chat. A existência do perfil não autoriza publicação.

`docs/retomada.md` é um registro histórico anterior, preservado como estava. Suas pendências antigas não substituem o diagnóstico e o progresso desta change.
