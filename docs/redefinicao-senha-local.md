# Redefinição de senha — primeira entrega local (Issue #131)

As políticas da change `redefinicao-senha-administrador` foram aprovadas pelo grupo na conversa de 07/11/2026. Esta entrega é limitada a contratos, estruturas locais e testes, na branch `feat/131-contratos-redefinicao-senha`. Não habilita a funcionalidade nem implementa telas.

## O que pode ser executado localmente

- `backend/contratos/redefinicao_senha.json`: contrato OpenAPI 3.1 com os dois POST e o GET somente leitura, entradas, respostas, autorização, erros e invariantes temporais.
- `sorrisomais/api_redefinicao_senha.py`: cliente dedicado com transporte injetável, validação estrita da projeção, erros sanitizados, Retry-After e `resultado_incerto`. Não repete requisições, não troca GET por POST e não copia mensagens técnicas do servidor. O transporte compartilhado atual não trata o204 público nem os códigos específicos; o adaptador separado evita alterar outros contratos.
- `sorrisomais/uuid7.py`: operação idempotente por UUIDv7. Não é token de sessão ou redefinição. Python 3.12.10 instalado não oferece `uuid.uuid7()`; timestamp48bits, versão/variante e aleatoriedade74bits são compostos com `datetime`, `uuid.UUID` e `secrets`, conforme RFC9562, sem nova dependência. Teste usa o vetor publicado da RFC, fronteiras e formato canônico. Sintaxe verificada para Python3.10; execução realizada em3.12.10, sem alegar teste em um interpretador3.10 ausente.
- `backend/contratos/redefinicao_senha.py`: referência executável **exclusivamente offline** para testar estados e invariantes com dados fictícios. Não é servidor Python, rota implantável ou substituto do backend Xano. RLock, rollback em memória e PBKDF2 para fixtures não provam transação, hash nativo ou timeout no Xano. Não possui sender, HTTP ou conexão a dados reais. Novas reservas ficam desligadas por padrão.
- Três schemas Xano locais aditivos: operação, controle e auditoria, além de versão de credencial nas definições de Conta de Acesso/Sessão. Não foram aplicados, compilados remotamente ou publicados; não existe handler de escrita Xano desta funcionalidade pronto para ativação.
- Flag `SORRISO_REDEFINICAO_HABILITADA=0` no exemplo e padrão da configuração. Valor inválido desabilita apenas o recurso e sinaliza configuração inválida; login/listagem não são desligados. Nenhuma tela lê essa nova propriedade nesta rodada.

## Contratos implementados no cliente

| Método e rota relativa | Comportamento local testado |
|---|---|
| POST `/contas-acesso/{conta_id}/redefinicoes-senha` | Intenção com UUIDv7, Bearer, resposta de sete campos e incerteza em timeout/resposta inesperada, sem retry. |
| GET `/contas-acesso/{conta_id}/redefinicoes-senha/{operacao_id}` | Somente leitura, sem corpo/query de segredo;404 não cria operação e nunca aciona POST. |
| POST `/auth/redefinicoes-senha/confirmar` | Código específico e senha sem trim;204 sem sessão,409/Retry-After e resposta perdida sem repetir troca. |

A referência local modela autorização de Administrador, cotas e cooldown, replay por30dias, ID antigo após remoção, deadline, estados independentes e terminais, consumo concorrente e rollback. Usa apenas contas/sessões fictícias fornecidas pelos testes. Não simula nem altera as rotas OTP/login reais. Modelar revogação de sessões fictícias não comprova revogação da instância.

## Verificações realizadas

No ambiente `.venv-win` foi instalado apenas `pytest==9.1.1`, já declarado em `requirements-dev.txt`, com suas dependências transitivas. Não houve mudança em Python, `requirements.txt` ou `requirements-dev.txt`.

```powershell
.venv-win/Scripts/python.exe -B -m pytest tests/test_uuid7.py tests/test_config_redefinicao_senha.py tests/test_redefinicao_backend_local.py tests/test_acesso.py -q -p no:cacheprovider
.venv-win/Scripts/python.exe -B -m pytest tests/api_contracts -q -p no:cacheprovider
$env:PYTHON_TEST_BIN = (Resolve-Path '.venv-win/Scripts/python.exe').Path
& 'C:/Program Files/nodejs/node.exe' --test tests/js/api_contracts/contas-acesso-redefinicoes-senha-post.test.mjs tests/js/api_contracts/contas-acesso-redefinicao-senha-get.test.mjs tests/js/api_contracts/auth-redefinicoes-senha-confirmar-post.test.mjs tests/js/api_contracts/contas-acesso-get.test.mjs
```

Resultados:132 testes Python do primeiro comando,259 do segundo e10 testes JavaScript passaram. Os testes por rota substituem o transporte HTTP; os JavaScript exercitam o cliente Python via subprocesso com rede substituída. Concorrência e resposta204 perdida são cenários locais. Nenhum teste foi enviado ao Xano, ao SendGrid ou a uma conta real.

## Pendências que impedem ativação

1. Reconciliar seletivamente os exports OTP/remetente com os responsáveis, preservando GUIDs e contratos; nenhuma definição remota foi importada como implementação nesta rodada.
2. Demonstrar primitiva transacional/CAS e timeout **total** real em ambiente isolado, com autorização específica. Não basta transportar o RLock ou resultados simulados para afirmar atomicidade remota.
3. Implementar e validar handlers/funções Xano dos contratos, coordenação com OTP e versão na emissão/validação de login; os schemas locais isolados não fazem isso.
4. Provar a compatibilidade mínima de OTP/link/login, invalidação cruzada, concorrência e revogação global. Política aprovada não equivale a código publicado compatível.
5. Confirmar configuração efetiva/verificação do remetente, proteções da cadeia de logs, URLHTTPS fixa e controle de ingresso. Nenhum envio será realizado para inferir funcionamento nesta etapa.

## Próxima rodada de frontend

Após revisão desta entrega, integrar cliente/configuração ao menu e à listagem existente sem retirar consulta da Recepcionista; oferecer envio/consulta de operação apenas ao Administrador, diálogo mascarado e tela pública antes do gate de login. Usar GET para resultado, estados separados e tratamento de confirmação incerta. A integração de telas poderá ser testada com transporte simulado, mas a flag real deve continuar desligada até concluir os gates de backend/implantação. Não publicar o diretório local sobre o workspace remoto incompleto.
