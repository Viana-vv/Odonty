# Design

## Decisão

O endpoint `POST /registros-clinicos` terá uma variável única para o
`consulta_id` efetivamente validado. Quando o payload informar `consulta_id`, o
backend valida Paciente e Profissional contra essa Consulta. Quando o payload
não informar Consulta, o backend procura uma Consulta do mesmo Paciente e
Profissional e usa o identificador encontrado apenas para manter o vínculo
consistente na gravação.

O filtro de autorização permanece no Xano. A interface continuará exibindo
somente Pacientes e Consultas devolvidos por `GET /consultas` e não tentará
fabricar Prontuário ou Consulta.

## Fluxo

1. Validar sessão, perfil profissional, Profissional ativo, Paciente ativo e
   Prontuário ativo.
2. Resolver a Consulta explícita ou uma Consulta no escopo do Profissional.
3. Gravar o Registro Clínico com o `consulta_id` resolvido.
4. Retornar confirmação segura; em 404, a interface informar que Paciente,
   Prontuário ou Consulta não foram encontrados no escopo permitido.

## Verificação

Os testes Python e JavaScript do contrato devem inspecionar a resolução do
identificador e a interface deve cobrir a mensagem segura. Nenhum teste fará
requisição de rede.

