import test from 'node:test';
import assert from 'node:assert/strict';
import { contractOperation, pythonAssertions } from './redefinicao-helpers.mjs';

test('GET resultado possui contrato autenticado separado da reserva', () => {
  const { operation } = contractOperation('GET', '/contas-acesso/{conta_id}/redefinicoes-senha/{operacao_id}');
  for (const status of [200, 400, 401, 403, 404, 503]) assert.ok(operation.responses[status]);
  assert.ok(operation.security?.length);
  assert.equal(operation.requestBody, undefined);
});

test('GET cliente consulta operação sem corpo e preserva dimensões independentes', () => pythonAssertions(`
http.side_effect = None
projecao.update(estado_envio='aceito', estado_link='consumido')
http.return_value = response(projecao)
assert cliente.consultar('sessao-ficticia', 12, operacao) == projecao
assert http.call_count == 1
args, kwargs = http.call_args
assert args[:2] == ('GET', 'https://exemplo.invalid/api:teste/contas-acesso/12/redefinicoes-senha/' + operacao)
assert kwargs.get('json') is None
assert kwargs.get('params') is None
assert kwargs['headers']['Authorization'] == 'Bearer sessao-ficticia'
`));

test('GET 404 e falha de conexão nunca disparam POST de criação', () => pythonAssertions(`
for resposta_api in [response({'codigo': 'OPERACAO_NAO_ENCONTRADA', 'mensagem': 'detalhe-nao-expor'}, 404), requests.ConnectionError('detalhe-nao-expor')]:
    http.reset_mock()
    http.side_effect = resposta_api if isinstance(resposta_api, Exception) else None
    http.return_value = resposta_api
    try:
        cliente.consultar('sessao-ficticia', 12, operacao)
        raise AssertionError('erro de consulta aceito')
    except api.ErroRedefinicaoSenha as erro:
        assert 'detalhe-nao-expor' not in str(erro)
    assert http.call_count == 1
    assert http.call_args.args[0] == 'GET'
`));
