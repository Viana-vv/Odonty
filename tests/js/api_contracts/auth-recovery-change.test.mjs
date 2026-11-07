import assert from 'node:assert/strict';
import test from 'node:test';
import { assertApiContract } from './helpers.mjs';

test('POST /auth/recuperacao-senha/trocar atualiza senha e invalida operação', () => {
  const source = assertApiContract('POST', '/auth/recuperacao-senha/trocar', 'api/sorriso_acesso/auth/recuperacao-senha-trocar_POST.xs');
  assert.match(source, /db\.edit conta_acesso/);
  assert.match(source, /senha: \$input\.senha/);
  assert.match(source, /utilizado: true/);
});
