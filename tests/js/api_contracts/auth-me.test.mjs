import assert from 'node:assert/strict';
import test from 'node:test';
import { assertApiContract } from './helpers.mjs';

test('GET /auth/me tem rota e export Xano correspondentes', () => {
  const source = assertApiContract('GET', '/auth/me', 'api/sorriso_acesso/auth/me_GET.xs');
  assert.match(source, /history\s*=\s*false/);
});
