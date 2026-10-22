import assert from 'node:assert/strict';
import test from 'node:test';
import { assertApiContract } from './helpers.mjs';

test('POST /auth/login tem rota e export Xano correspondentes', () => {
  const source = assertApiContract('POST', '/auth/login', 'api/sorriso_acesso/auth/login_POST.xs');
  assert.match(source, /history\s*=\s*false/);
  assert.match(source, /intersect:\["administrador", "recepcionista", "profissional", "paciente"\]/);
  assert.match(source, /security\.check_password/);
  assert.match(source, /\$conta\.situacao != "ativo"/);
});
