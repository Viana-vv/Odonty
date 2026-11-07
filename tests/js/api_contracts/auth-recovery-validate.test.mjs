import assert from 'node:assert/strict';
import test from 'node:test';
import { assertApiContract } from './helpers.mjs';

test('POST /auth/recuperacao-senha/validar controla tentativas e expiração', () => {
  const source = assertApiContract('POST', '/auth/recuperacao-senha/validar', 'api/sorriso_acesso/auth/recuperacao-senha-validar_POST.xs');
  assert.match(source, /security\.check_password/);
  assert.match(source, /tentativas >= 5/);
  assert.match(source, /expira_em <= now/);
});
