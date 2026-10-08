import test from 'node:test';
import assert from 'node:assert/strict';
import { assertApiContract } from './helpers.mjs';

test('cliente declara POST /consultas', () => {
  const source = assertApiContract('POST', '/consultas', 'api/sorriso_acesso/consultas_POST.xs');
  assert.doesNotMatch(source, /\s in \s/);
  assert.doesNotMatch(source, /\|default:/);
  assert.match(source, /db\.get procedimento/);
});
