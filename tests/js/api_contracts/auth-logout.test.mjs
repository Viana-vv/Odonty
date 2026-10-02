import assert from 'node:assert/strict';
import test from 'node:test';
import { assertApiContract } from './helpers.mjs';

test('POST /auth/logout tem rota e export Xano correspondentes', () => {
  const source = assertApiContract('POST', '/auth/logout', 'api/sorriso_acesso/auth/logout_POST.xs');
  assert.match(source, /history\s*=\s*false/);
});
