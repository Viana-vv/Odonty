import test from 'node:test';
import assert from 'node:assert/strict';
import { contractOperation, pythonAssertions } from './redefinicao-helpers.mjs';

test('POST confirmação é público com204 e erros previstos', () => {
  const { operation } = contractOperation('POST', '/auth/redefinicoes-senha/confirmar');
  for (const status of [204, 400, 409, 429, 503]) assert.ok(operation.responses[status]);
  assert.deepEqual(operation.security, []);
});

test('POST confirmação preserva espaços da senha e não autentica sessão', () => pythonAssertions(`
http.side_effect = None
http.return_value = response(status=204)
senha = '  senha ficticia longa  '
assert cliente.confirmar('A' * 43, senha) is None
assert http.call_count == 1
args, kwargs = http.call_args
assert args[:2] == ('POST', 'https://exemplo.invalid/api:teste/auth/redefinicoes-senha/confirmar')
assert kwargs['json'] == {'codigo': 'A' * 43, 'senha': senha}
assert 'Authorization' not in kwargs['headers']
assert kwargs['allow_redirects'] is False
`));

test('POST409 informa espera e resposta perdida permanece incerta sem retry', () => pythonAssertions(`
http.side_effect = None
http.return_value = response({'codigo': 'ENVIO_EM_PROCESSAMENTO', 'mensagem': 'detalhe-interno'}, 409, {'Retry-After': '20'})
try:
    cliente.confirmar('A' * 43, 'senha ficticia longa')
    raise AssertionError('409 aceito')
except api.ErroRedefinicaoSenha as erro:
    assert erro.status == 409 and erro.codigo == 'ENVIO_EM_PROCESSAMENTO'
    assert erro.retry_after == 20 and not erro.resultado_incerto
assert http.call_count == 1
http.reset_mock()
http.side_effect = requests.ConnectionError('resposta204 perdida apos commit ficticio')
try:
    cliente.confirmar('A' * 43, 'senha ficticia longa')
    raise AssertionError('perda de resposta aceita')
except api.ErroRedefinicaoSenha as erro:
    assert erro.resultado_incerto
assert http.call_count == 1
`));
