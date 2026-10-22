import assert from 'node:assert/strict';
import test from 'node:test';
import { assertApiContract } from './helpers.mjs';

test('GET /auth/me tem rota e export Xano correspondentes', () => {
  const source = assertApiContract('GET', '/auth/me', 'api/sorriso_acesso/auth/me_GET.xs');
  assert.match(source, /history\s*=\s*false/);
  assert.match(source, /intersect:\["administrador", "recepcionista", "profissional", "paciente"\]/);
  assert.match(source, /\$conta\.situacao != "ativo"/);
  assert.match(source, /sorriso_validar_sessao/);
});
