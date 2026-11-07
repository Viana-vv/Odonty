import test from 'node:test';
import assert from 'node:assert/strict';
import { contractOperation, pythonAssertions } from './redefinicao-helpers.mjs';

test('POST administrativo possui contrato de resposta e erros sem publicação remota', () => {
  const { operation } = contractOperation('POST', '/contas-acesso/{conta_id}/redefinicoes-senha');
  for (const status of [200, 400, 401, 403, 404, 409, 429, 503]) assert.ok(operation.responses[status]);
  assert.ok(operation.security?.length, 'reserva exige autenticação administrativa');
});

test('POST cliente envia somente intenção e Bearer uma vez, sem dados do destinatário', () => pythonAssertions(`
http.side_effect = None
http.return_value = response(projecao)
assert cliente.solicitar('sessao-ficticia', 12, operacao) == projecao
assert http.call_count == 1
args, kwargs = http.call_args
assert args[:2] == ('POST', 'https://exemplo.invalid/api:teste/contas-acesso/12/redefinicoes-senha')
assert kwargs['json'] == {'operacao_id': operacao}
assert kwargs['headers']['Authorization'] == 'Bearer sessao-ficticia'
assert kwargs['allow_redirects'] is False
`));

test('POST não repete após timeout nem retorna segredos de resposta incompatível', () => pythonAssertions(`
http.side_effect = requests.Timeout('segredo-do-provedor')
try:
    cliente.solicitar('sessao-ficticia', 12, operacao)
    raise AssertionError('timeout aceito')
except api.ErroRedefinicaoSenha as erro:
    assert 'segredo-do-provedor' not in str(erro)
assert http.call_count == 1
http.reset_mock()
http.side_effect = None
http.return_value = response({**projecao, 'codigo': 'segredo-proibido'})
try:
    cliente.solicitar('sessao-ficticia', 12, operacao)
    raise AssertionError('projecao com segredo aceita')
except api.ErroRedefinicaoSenha:
    pass
assert http.call_count == 1
`));
